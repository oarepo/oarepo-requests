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

from invenio_drafts_resources.records.api import Record
from invenio_requests.proxies import current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_requests.services.requests.results import RequestList

    from oarepo_requests.services.results import RequestTypesList
    from oarepo_requests.typing import EntityReference


def search_requests(identity: Identity, record: Record | EntityReference, expand: bool = False) -> RequestList:
    """Search requests for a given record."""
    topic_ref = ResolverRegistry.reference_entity(record) if isinstance(record, Record) else record
    return cast("RequestList", current_requests_service.search(identity, topic=topic_ref, expand=expand))


def applicable_requests(identity: Identity, record: Record | EntityReference) -> RequestTypesList:
    """Get applicable request types for a record."""
    topic_ref = ResolverRegistry.reference_entity(record) if isinstance(record, Record) else record
    return current_requests_service.applicable_request_types(identity, topic=topic_ref)
