from __future__ import annotations

from typing import TYPE_CHECKING

from oarepo_requests.typing import EntityReference
from invenio_requests.proxies import current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_drafts_resources.records.api import Record

if TYPE_CHECKING:
    from flask_principal import Identity


def search_requests(
    identity: Identity, record: Record | EntityReference, expand: bool = False
):
    topic_ref = (
        ResolverRegistry.reference_entity(record)
        if isinstance(record, Record)
        else record
    )
    return current_requests_service.search(identity, topic=topic_ref, expand=expand)


def applicable_requests(identity: Identity, record: Record | EntityReference):
    topic_ref = (
        ResolverRegistry.reference_entity(record)
        if isinstance(record, Record)
        else record
    )
    return current_requests_service.applicable_request_types(identity, topic=topic_ref)
