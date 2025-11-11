#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Snapshot component for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override
from uuid import UUID

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_requests.proxies import current_requests_service
from invenio_search.engine import dsl

from oarepo_requests.utils import reference_entity

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record


class RecordSnapshotComponent(ServiceComponent):
    """Snapshot component for requests."""

    def create_snapshot(self, record: Record) -> None:
        """Create snapshot for the record."""
        topic_dict = reference_entity(record)
        topic_type, topic_id = next(iter(topic_dict.items()))

        # find request for this record
        # TODO: is this tested?
        requests = list(
            current_requests_service.search(
                system_identity,
                extra_filter=dsl.Q(
                    "bool",
                    must=[
                        dsl.Q("term", **{f"topic.{topic_type}": topic_id}),
                        dsl.Q("terms", type=current_app.config["PUBLISH_REQUEST_TYPES"]),
                    ],
                ),
                sort="newest",
                size=1,
            ).hits
        )

        if requests:
            from oarepo_requests.snapshots import create_snapshot_and_possible_event

            create_snapshot_and_possible_event(record, record["metadata"], UUID(requests[0]["id"]))

    @override
    def update(self, identity: Identity, *, record: Record, **kwargs: Any) -> None:
        """Update handler."""
        self.create_snapshot(record)

    @override
    def update_draft(self, identity: Identity, *, record: Record, **kwargs: Any) -> None:  # type: ignore[reportIncompatibleMethodOverride]
        self.create_snapshot(record)
