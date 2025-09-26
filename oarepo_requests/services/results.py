#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Results components for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flask_principal import Identity
from invenio_records_resources.records import Record

from invenio_records_resources.services import LinksTemplate
from invenio_requests.customizations import RequestType
from oarepo_runtime.services.results import RecordList
from oarepo_requests.services.schema import RequestTypeSchema

if TYPE_CHECKING:
    from collections.abc import Iterator
    from invenio_records_resources.records.api import Record
    from marshmallow import Schema


class RequestTypesListDict(dict):
    """List of request types dictionary with additional topic."""

    topic = None


class RequestTypesList(RecordList):
    """An in-memory list of request types compatible with opensearch record list."""

    def __init__(self, *args: Any, record: Record | None = None, schema: Schema | None=None, **kwargs: Any) -> None:
        """Initialize the list of request types."""
        self._record = record
        super().__init__(*args, **kwargs)
        self._schema = schema or RequestTypeSchema

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        hits = list(self.hits)
        res = RequestTypesListDict(
            hits={
                "hits": hits,
                "total": self.total,
            }
        )
        if self._links_tpl: # TODO: pass1: query params in link?
            res["links"] = self._links_tpl.expand(self._identity, None)
        res.topic = self._record
        return res

    @property
    def hits(self) -> Iterator[dict]:
        """Iterator over the hits."""
        for hit in self._results:
            # Project the record
            projection = self._schema(
                context={
                    "identity": self._identity,
                    "record": self._record,
                }
            ).dump(
                hit,
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(self._identity, hit)
            yield projection

    @property
    def total(self) -> int:
        """Total number of hits."""
        return len(self._results)


def serialize_request_types(
    request_types: dict[str, RequestType], identity: Identity, record: Record
) -> list[RequestTypeSchema]:
    """Serialize request types.

    :param request_types: Request types to serialize.
    :param identity: Identity of the user.
    :param record: Record for which the request types are serialized.
    :return: List of serialized request types.
    """
    return [
        RequestTypeSchema(context={"identity": identity, "record": record}).dump(
            request_type
        )
        for request_type in request_types.values()
    ]
