#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Results components for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from invenio_records_resources.records import Record
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_requests.services.results import EntityResolverExpandableField
from oarepo_runtime.services.results import RecordList

from oarepo_requests.services.schema import (
    RequestTypeSchema,
    request_type_identity_ctx,
    request_type_record_ctx,
)
from oarepo_requests.utils import string_to_reference

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services.records.service import RecordService
    from invenio_requests.customizations import RequestType


class StringEntityResolverExpandableField(EntityResolverExpandableField):
    """Expandable entity resolver field.

    It will use the Entity resolver registry to retrieve the service to
    use to fetch records and the fields to return when serializing
    the referenced record.
    """

    def get_value_service(self, value: str) -> tuple[str, RecordService]:  # type: ignore[override]
        """Return the value and the service via entity resolvers."""
        ref = string_to_reference(value)
        v, service = super().get_value_service(ref)
        return v, service


class RequestTypesListDict(dict):
    """List of request types dictionary with additional topic."""

    topic: Record | None = None


class RequestTypesList(RecordList):
    """An in-memory list of request types compatible with opensearch record list."""

    def __init__(
        self,
        *args: Any,
        record: Record | None = None,
        schema: ServiceSchemaWrapper | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the list of request types."""
        self._record = record
        super().__init__(*args, **kwargs)
        self._schema = schema or ServiceSchemaWrapper(self._service, RequestTypeSchema)

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        hits = list(self.hits)
        res = RequestTypesListDict(
            hits={
                "hits": hits,
                "total": self.total,
            }
        )
        if self._links_tpl:
            res["links"] = self._links_tpl.expand(self._identity, None)
        res.topic = self._record
        return res

    @property
    def hits(self) -> Iterator[dict]:
        """Iterator over the hits."""
        for hit in self._results:
            # Project the record
            tok_identity = request_type_identity_ctx.set(self._identity)
            tok_record = request_type_record_ctx.set(self._record)
            try:
                # identity in context is hardcoded in ServiceSchemaWrapper
                # which we have to use if we want to subclass RecordList
                projection = self._schema.dump(
                    hit, context={"identity": self._identity}
                )
            finally:
                # Reset contextvars to previous values to avoid leaking state
                request_type_identity_ctx.reset(tok_identity)
                request_type_record_ctx.reset(tok_record)

            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(self._identity, hit)
            yield projection

    @property
    def total(self) -> int:
        """Total number of hits."""
        return len(self._results)


def serialize_request_types(
    request_types: dict[str, RequestType], identity: Identity, record: Record
) -> list[dict[str, Any]]:
    """Serialize request types.

    :param request_types: Request types to serialize.
    :param identity: Identity of the user.
    :param record: Record for which the request types are serialized.
    :return: List of serialized request types.
    """
    # contextvars approach from gpt
    tok_identity = request_type_identity_ctx.set(identity)
    tok_record = request_type_record_ctx.set(record)
    try:
        return [
            cast("dict[str, Any]", RequestTypeSchema().dump(request_type))
            for request_type in request_types.values()
        ]
    finally:
        # Reset contextvars to previous values to avoid leaking state
        request_type_identity_ctx.reset(tok_identity)
        request_type_record_ctx.reset(tok_record)
