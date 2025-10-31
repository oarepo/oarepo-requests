#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for publishing draft requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_i18n import _
from invenio_requests.records.api import Request

from oarepo_requests.errors import UnresolvedRequestsError, VersionAlreadyExists

from ..utils import get_draft_record_service, search_requests
from .generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestAction
else:
    RequestAction = object


class PublishMixin(RequestAction):
    """Mixin for publish actions."""

    def can_execute(self) -> bool:
        """Check if the action can be executed."""
        if not super().can_execute():
            return False

        try:
            from ..types.publish_draft import PublishDraftRequestType

            topic = self.request.topic.resolve()
            PublishDraftRequestType.validate_topic(system_identity, topic)
        except:  # noqa E722: used for displaying buttons, so ignore errors here
            return False
        return True


# TODO: snapshot
class PublishDraftSubmitAction(PublishMixin, OARepoSubmitAction):
    """Submit action for publishing draft requests."""

    @override
    def apply(
        self,
        identity: Identity,
        topic: Record,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if "payload" in self.request and "version" in self.request["payload"]:
            topic_service = get_draft_record_service(topic)
            versions = topic_service.search_versions(identity, topic.pid.pid_value)
            versions_hits = versions.to_dict()["hits"]["hits"]
            for rec in versions_hits:
                if "version" in rec["metadata"]:
                    version = rec["metadata"]["version"]
                    if version == self.request["payload"]["version"]:
                        raise VersionAlreadyExists
            topic.metadata["version"] = self.request["payload"]["version"]
        # TODO: notification


class PublishDraftAcceptAction(PublishMixin, OARepoAcceptAction):
    """Accept action for publishing draft requests."""

    name = _("Publish")

    @override
    def apply(
        self,
        identity: Identity,
        topic: Record,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        topic_service = get_draft_record_service(topic)
        requests = search_requests(system_identity, topic)

        for result in requests._results:  # noqa SLF001
            if (
                result.type
                not in [
                    "publish_draft",
                    "publish_new_version",
                    "publish_changed_metadata",
                ]
                and result.is_open
                and Request.get_record(result.uuid)["status"]
                in (
                    "submitted",
                    "created",
                )
            ):
                # note: we can not use solely the result.is_open because changes may not be committed yet
                # to opensearch index. That's why we need to get the record from DB and re-check.
                raise UnresolvedRequestsError(action=str(self.name))
        id_ = topic["id"]

        topic_service.publish(identity, id_, *args, uow=uow, expand=False, **kwargs)
        # TODO: notification


class PublishDraftDeclineAction(OARepoDeclineAction):
    """Decline action for publishing draft requests."""

    name = _("Return for correction")
