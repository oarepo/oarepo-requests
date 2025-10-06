#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Results components for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from invenio_pidstore.errors import PIDDeletedError
from invenio_rdm_records.services.services import RDMRecordService
from invenio_records_permissions.api import permission_filter
from invenio_records_resources.records import Record
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_requests.services.results import EntityResolverExpandableField
from invenio_search import current_search_client
from invenio_search.engine import dsl
from oarepo_runtime.services.results import RecordList
from sqlalchemy.exc import NoResultFound

from oarepo_requests.services.schema import (
    RequestTypeSchema,
    request_type_identity_ctx,
    request_type_record_ctx,
)
from oarepo_requests.utils import resolve_reference_dict, string_to_reference

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_records_resources.services.records.config import SearchOptions
    from invenio_records_resources.services.records.service import RecordService
    from invenio_requests.customizations import RequestType
    from invenio_search import RecordsSearchV2
    from opensearch_dsl.response import Response


class ReadManyDraftsService(RDMRecordService):
    """Service rewriting read_many to return drafts instead of published records.

    Implemented to use in expandable fields.
    """

    def __eq__(self, other: object) -> bool:
        """Services are equal if they are the same type and share the same config object."""
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        return cast(
            "bool",
            self.config.service_id == other.config.service_id,  # type: ignore[attr-defined]
        )  # TODO: service has no attribute config, also has service_id as Optional?

    def __hash__(self) -> int:
        """Hash based on service type and its config object identity."""
        return hash(self.config.service_id)

    @override
    def create_search(
        self,
        identity: Identity,
        record_cls: type[Record],
        search_opts: type[SearchOptions],
        permission_action: str = "read",
        preference: str | None = None,
        extra_filter: dsl.query.Query | None = None,
        versioning: bool = True,
    ) -> RecordsSearchV2:
        """Instantiate a search class."""
        if permission_action:
            permission = self.permission_policy(action_name=permission_action, identity=identity)
        else:
            permission = None

        default_filter = permission_filter(permission)
        if extra_filter is not None:
            default_filter = default_filter & extra_filter

        search = search_opts.search_cls(
            using=current_search_client,
            default_filter=default_filter,
            index=record_cls.index._name,  # noqa SLF001  # TODO: changed; check if necessary
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
        return search.extra(**extras)

    @override
    def _read_many(
        self,
        identity: Identity,
        search_query: dsl.query.Query,
        fields: list[str] | None = None,
        max_records: int = 150,
        record_cls: type[Record] | None = None,
        search_opts: type[SearchOptions] | None = None,
        extra_filter: dsl.query.Query | None = None,
        preference: str | None = None,
        sort: str | None = None,  # TODO: ?
        **kwargs: Any,
    ) -> Response:
        """Search for records matching the ids."""
        # We use create_search() to avoid the overhead of aggregations etc
        # being added to the query with using search_request().
        search = self.create_search(
            identity=identity,
            record_cls=record_cls or self.draft_cls,
            search_opts=search_opts or self.config.search_drafts,
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
        return search.execute()

    @override
    def read_many(
        self, identity: Identity, ids: list[str], fields: list[str] | None = None, **kwargs: Any
    ) -> RecordList:
        """Search for records matching the ids."""
        clauses = [dsl.Q("term", id=id_) for id_ in ids]
        query = dsl.Q("bool", minimum_should_match=1, should=clauses)

        results = self._read_many(
            identity,
            query,
            fields,
            len(ids),
            record_cls=self.draft_cls,
            search_opts=self.config.search_drafts,
            permission_action="read_draft",
            **kwargs,
        )

        return cast(
            "RecordList",
            self.result_list(
                self,
                identity,
                results,
                links_item_tpl=self.links_item_tpl,
            ),
        )


class DraftAwareEntityResolverExpandableField(EntityResolverExpandableField):
    """Expandable entity resolver field capable of resolving drafts."""

    def get_value_service(self, value: dict[str, str]) -> tuple[str, RecordService]:
        """Return the value and the service via entity resolvers."""
        v, service = super().get_value_service(value)
        try:  # TODO: hack: draft might get deleted ie in case of publish; then the service returns published record
            record = resolve_reference_dict(value)
        except (NoResultFound, PIDDeletedError):
            return "", service
        if record.is_draft:
            service = ReadManyDraftsService(service.config)
        return v, service


class StringEntityResolverExpandableField(EntityResolverExpandableField):
    """Expandable entity resolver field.

    It will use the Entity resolver registry to retrieve the service to
    use to fetch records and the fields to return when serializing
    the referenced record.
    """

    #  the message is: Argument 1 of "get_value_service" is incompatible with supertype
    #  "DraftAwareEntityResolverExpandableField"; supertype defines the argument type as "dict[str, str]"  [override]
    # invenio doesn't allow to implement this differently?
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
        if self._links_tpl:  # TODO: pass1: query params in link?
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
                projection = self._schema.dump(hit, context={"identity": self._identity})
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
        return [RequestTypeSchema().dump(request_type) for request_type in request_types.values()]
    finally:
        # Reset contextvars to previous values to avoid leaking state
        request_type_identity_ctx.reset(tok_identity)
        request_type_record_ctx.reset(tok_record)
