#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Component for creating record snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
from uuid import UUID

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components.base import ServiceComponent
from invenio_requests.proxies import current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from opensearch_dsl.query import Bool, Term, Terms

if TYPE_CHECKING:
    from typing import Any

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record


class RecordSnapshotComponent(ServiceComponent):
    """Component for handling record snapshots."""

    def create_snapshot(self, record: Record) -> None:
        """Create snapshot for the record."""
        topic_dict = ResolverRegistry.reference_entity(record)
        topic_type, topic_id = next(iter(topic_dict.items()))

        # find request for this record
        requests = list(
            current_requests_service.search(
                system_identity,
                extra_filter=Bool(
                    must=[
                        Term(**{f"topic.{topic_type}": topic_id}),
                        Terms(type=current_app.config["PUBLISH_REQUEST_TYPES"]),
                    ]
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
        """Create snapshot on update call."""
        self.create_snapshot(record)

    # TODO: technically we have subclassed service for drafts, so to be really consistent we should also have
    # separate components?
    @override
    def update_draft(self, identity: Identity, *, record: Record, **kwargs: Any) -> None:
        """Create snapshot on update draft call."""
        self.create_snapshot(record)
