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

from invenio_requests.customizations import RequestType
from oarepo_runtime.services.results import RecordList
from oarepo_requests.services.schema import RequestTypeSchema
from invenio_requests.services.results import EntityResolverExpandableField
from invenio_rdm_records.services.services import RDMRecordService
from oarepo_requests.utils import string_to_reference, resolve_reference_dict

from invenio_records_permissions.api import permission_filter
from invenio_search import current_search_client
from invenio_search.engine import dsl


if TYPE_CHECKING:
    from collections.abc import Iterator
    from invenio_records_resources.records.api import Record
    from marshmallow import Schema

class ReadManyDraftsService(RDMRecordService):
    def __eq__(self, other: object) -> bool:
        """Services are equal if they are the same type and share the same config object."""
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        return self.config.service_id == other.config.service_id

    def __hash__(self) -> int:
        """Hash based on service type and its config object identity."""
        return hash(self.config.service_id)

    def create_search(
        self,
        identity,
        record_cls,
        search_opts,
        permission_action="read",
        preference=None,
        extra_filter=None,
        versioning=True,
    ):
        """Instantiate a search class."""
        if permission_action:
            permission = self.permission_policy(
                action_name=permission_action, identity=identity
            )
        else:
            permission = None

        default_filter = permission_filter(permission)
        if extra_filter is not None:
            default_filter = default_filter & extra_filter

        search = search_opts.search_cls(
            using=current_search_client,
            default_filter=default_filter,
            index=record_cls.index._name, # TODO: changed
        )

        search = (
            search
            # Avoid query bounce problem
            .with_preference_param(preference)
        )

        if versioning:
            search = (
                search
                # Add document version to search response
                .params(version=True)
            )

        # Extras
        extras = {}
        extras["track_total_hits"] = True
        search = search.extra(**extras)

        return search


    def _read_many(
        self,
        identity,
        search_query,
        fields=None,
        max_records=150,
        record_cls=None,
        search_opts=None,
        extra_filter=None,
        preference=None,
        sort=None,
        **kwargs,
    ):
        """Search for records matching the ids."""
        # We use create_search() to avoid the overhead of aggregations etc
        # being added to the query with using search_request().
        search = self.create_search(
            identity=identity,
            record_cls=record_cls,
            search_opts=search_opts,
            permission_action="read_draft",
            preference=preference,
            extra_filter=extra_filter,
            versioning=True,
        )

        # Fetch only certain fields - explicitly add internal system fields
        # required to use the result list to dump the output.
        if fields:
            dumper_fields = ["uuid", "version_id", "created", "updated", "expires_at"]
            fields = fields + dumper_fields
            # ES 7.11+ supports a more efficient way of fetching only certain
            # fields using the "fields"-option to a query. However, ES 7 and
            # OS 1 versions does not support it, so we use the source filtering
            # method instead for now.
            search = search.source(fields)

        search = search[0:max_records].query(search_query)
        if sort:
            search = search.sort(sort)
        search_result = search.execute()

        return search_result

    def read_many(self, identity, ids, fields=None, **kwargs):
        """Search for records matching the ids."""
        clauses = []
        for id_ in ids:
            clauses.append(dsl.Q("term", **{"id": id_}))
        query = dsl.Q("bool", minimum_should_match=1, should=clauses)

        results = self._read_many(identity,
                                  query,
                                  fields,
                                  len(ids),
                                  record_cls=self.draft_cls,
                                  search_opts=self.config.search_drafts,
                                  permission_action="read_draft",
                                  **kwargs)

        return self.result_list(
            self,
            identity,
            results,
            links_item_tpl=self.links_item_tpl,
        )

class DraftAwareEntityResolverExpandableField(EntityResolverExpandableField):

    def get_value_service(self, value):
        """Return the value and the service via entity resolvers."""
        v, service = super().get_value_service(value)
        record = resolve_reference_dict(value)
        if record.is_draft:
            service = ReadManyDraftsService(service.config)
        return v, service

class StringDraftAwareEntityResolverExpandableField(DraftAwareEntityResolverExpandableField):
    """Expandable entity resolver field.

    It will use the Entity resolver registry to retrieve the service to
    use to fetch records and the fields to return when serializing
    the referenced record.
    """

    def get_value_service(self, value: str):
        """Return the value and the service via entity resolvers."""
        ref = string_to_reference(value)
        v, service = super().get_value_service(ref)
        return v, service


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
