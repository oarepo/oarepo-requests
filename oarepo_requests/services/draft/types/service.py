#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Draft record request types service."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from oarepo_requests.services.record.types.service import RecordRequestTypesService

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records.api import Record

    from oarepo_requests.services.results import RequestTypesList


class DraftRecordRequestTypesService(RecordRequestTypesService):
    """Draft record request types service.

    This service sits on /model/draft/id/applicable-requests endpoint and provides a list of request types.
    """

    @property
    def draft_cls(self) -> type[Record]:
        """Factory for creating a record class."""
        return self.record_service.config.draft_cls

    @override
    def get_applicable_request_types(
        self, identity: Identity, record_id: str
    ) -> RequestTypesList:
        record = self.draft_cls.pid.resolve(record_id, registered_only=False)
        return self._get_applicable_request_types(identity, record)
