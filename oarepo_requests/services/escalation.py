#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Links Module for requests."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests import current_events_service
from invenio_requests.proxies import current_requests_service
from invenio_requests.records import Request
from invenio_requests.records.models import RequestEventModel
from oarepo_workflows.proxies import current_oarepo_workflows

from oarepo_requests.notifications.builders.escalate import EscalateRequestSubmitNotificationBuilder
from oarepo_requests.types.events.escalation import EscalationEventType

if TYPE_CHECKING:
    from collections.abc import Generator

    from invenio_db.uow import UnitOfWork
    from oarepo_workflows import WorkflowRequestEscalation

logger = logging.getLogger(__name__)


@unit_of_work()
def escalate_request(request: Request, escalation: WorkflowRequestEscalation, uow: UnitOfWork) -> None:
    """Escalate single request and commit the change to the database."""
    logger.info("Escalating request %s", request.id)
    resolved_topic = request.topic.resolve()
    receiver = escalation.recipient_entity_reference(record=resolved_topic)

    old_receiver_str = json.dumps(
        request["receiver"], sort_keys=True
    )  # why sort keys? should be only one even in multiple recipients
    new_receiver_str = json.dumps(receiver, sort_keys=True)
    if new_receiver_str != old_receiver_str:
        logger.info("Request %s receiver changed from %s to %s", request.id, old_receiver_str, new_receiver_str)

        data = {
            "payload": {
                "old_receiver": old_receiver_str,
                "new_receiver": new_receiver_str,
                "escalation": escalation.escalation_id,
            }
        }

        current_events_service.create(
            system_identity,
            str(request.id),
            data,
            event_type=EscalationEventType,
            uow=uow,
        )

        request.receiver = receiver
        # done in RecordCommitOp? request.commit()
        uow.register(NotificationOp(EscalateRequestSubmitNotificationBuilder.build(request=request)))  # type: ignore[reportArgumentType]
        logger.info("Notification mail sent to %s", new_receiver_str)
        uow.register(RecordCommitOp(request))  # type: ignore[reportArgumentType]


def check_escalations() -> None:
    """Check and escalate all stale requests, if after time delta is reached."""
    for request, escalation in stale_requests():
        escalate_request(request, escalation)


def stale_requests() -> Generator[tuple[Request, WorkflowRequestEscalation]]:
    """Yield all submitted requests with expired time of escalation."""
    hits = current_requests_service.scan(system_identity, params={"is_open": True})
    for hit in hits:
        # with (suppress(Exception)):
        r = Request.get_record(hit["id"])
        request_type = r.type.type_id
        topic = r.topic.resolve()
        workflow = current_oarepo_workflows.get_workflow(topic)
        workflow_request = workflow.requests()[request_type]

        if workflow_request.escalations:
            escalation_events = (
                db.session.query(RequestEventModel)
                # typing bool issue with SQLAlchemy; idk how to fix this
                # relevant probably https://stackoverflow.com/questions/76387837/sqlalchemy-typing-support-on-filter-for-imperatively-mapped-attrs-classes
                .filter(RequestEventModel.type == "E", RequestEventModel.request_id == r.id)  # type: ignore[reportArgumentType]
                .all()
            )

            event_escalation_ids = {cast("dict[str, Any]", e.json)["payload"]["escalation"] for e in escalation_events}
            sorted_escalations = [
                e
                for e in sorted(workflow_request.escalations, key=lambda escalation: escalation.after)
                if e.escalation_id not in event_escalation_ids
            ]

            most_recent_escalation = None

            for escalation in sorted_escalations:
                # take the most recent one
                utc_now_naive = datetime.now(UTC).replace(tzinfo=None)
                if (
                    cast("datetime", r.updated) + escalation.after <= utc_now_naive
                ):  # for some reason request is not timezone aware
                    most_recent_escalation = escalation
                else:
                    break

            if most_recent_escalation:
                yield r, most_recent_escalation
