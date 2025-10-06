#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing utility functions for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from invenio_drafts_resources.records.api import Record as RecordWithDraft
from invenio_drafts_resources.services.records.service import RecordService
from oarepo_runtime import current_runtime

from oarepo_requests.proxies import current_requests_service
from oarepo_requests.utils import reference_entity

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_requests.services.requests.results import RequestList

    from oarepo_requests.services.results import RequestTypesList


def search_requests(identity: Identity, record: RecordWithDraft | dict[str, str], expand: bool = False) -> RequestList:
    """Search requests for a given record."""
    topic_ref = reference_entity(record) if isinstance(record, RecordWithDraft) else record
    return cast("RequestList", current_requests_service.search(identity, topic=topic_ref, expand=expand))


def applicable_requests(identity: Identity, record: RecordWithDraft | dict[str, str]) -> RequestTypesList:
    """Get applicable request types for a record."""
    topic_ref = reference_entity(record) if isinstance(record, RecordWithDraft) else record
    return current_requests_service.applicable_request_types(identity, topic=topic_ref)


def get_draft_record_service(record: Record) -> RecordService:
    """Get the draft record service for a record and checks it supports drafts."""
    topic_service = current_runtime.get_record_service_for_record(record)
    if not topic_service:
        raise KeyError(f"Record {record} service not found")
    if not isinstance(topic_service, RecordService):
        raise TypeError("Draft service required for editing records.")
    return topic_service
