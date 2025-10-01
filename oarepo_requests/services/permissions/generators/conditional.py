#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Conditional generators for needs based on request type, event type, and requester role."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from flask_principal import Identity
from invenio_records_permissions.generators import ConditionalGenerator, Generator
from invenio_records_resources.references.entity_resolvers import EntityProxy
from invenio_requests.resolvers.registry import ResolverRegistry
from oarepo_runtime.proxies import current_runtime
from oarepo_workflows.requests import RecipientGeneratorMixin
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestType
    from opensearch_dsl.query import Query


class IfRequestedBy(RecipientGeneratorMixin, ConditionalGenerator):
    """Conditional generator that generates needs when a request is made by a given requester role."""

    def __init__(
        self,
        requesters: list[Generator] | tuple[Generator] | Generator,
        then_: list[Generator],
        else_: list[Generator],
    ) -> None:
        """Initialize the generator."""
        super().__init__(then_, else_)
        if not isinstance(requesters, (list, tuple)):
            requesters = [requesters]
        self.requesters = requesters

    def _condition(
        self,
        *,
        request_type: RequestType,
        creator: Identity | EntityProxy | Any,
        **kwargs: Any,
    ) -> bool:
        """Condition to choose generators set."""
        # get needs
        if isinstance(creator, Identity):
            needs = creator.provides
        else:
            if not isinstance(creator, EntityProxy):
                creator = ResolverRegistry.reference_entity(creator)
            needs = creator.get_needs()

        for condition in self.requesters:
            condition_needs = set(condition.needs(request_type=request_type, creator=creator, **kwargs))
            condition_excludes = set(condition.excludes(request_type=request_type, creator=creator, **kwargs))

            if not condition_needs.intersection(needs):
                continue
            if condition_excludes and condition_excludes.intersection(needs):
                continue
            return True
        return False

    def reference_receivers(
        self,
        record: Record | None = None,
        request_type: RequestType | None = None,
        **context: Any,
    ) -> list[dict[str, str]]:  # pragma: no cover
        """Return the reference receiver(s) of the request.

        This call requires the context to contain at least "record" and "request_type"

        Must return a list of dictionary serialization of the receivers.

        Might return empty list or None to indicate that the generator does not
        provide any receivers.
        """
        ret = []
        for gen in self._generators(record=record, request_type=request_type, **context):
            if isinstance(gen, RecipientGeneratorMixin):
                ret.extend(gen.reference_receivers(record=record, request_type=request_type, **context))
        return ret

    def query_filter(self, **context: Any) -> Query:
        """Search filters."""
        raise NotImplementedError("Please use IfRequestedBy only in recipients, not elsewhere.")


class IfNoNewVersionDraft(ConditionalGenerator):
    """Generator that checks if the record has no new version draft."""

    def __init__(self, then_: list[Generator], else_: list[Generator] | None = None) -> None:
        """Initialize the generator."""
        else_ = [] if else_ is None else else_
        super().__init__(then_, else_=else_)

    @override
    def _condition(self, record: Record, **kwargs: Any) -> bool:
        if hasattr(record, "is_draft"):
            is_draft = record.is_draft
        else:
            return False
        if hasattr(record, "versions"):
            next_draft_id = record.versions.next_draft_id
        else:
            return False
        return not is_draft and not next_draft_id


class IfNoEditDraft(ConditionalGenerator):
    """Generator that checks if the record has no edit draft."""

    def __init__(self, then_: list[Generator], else_: list[Generator] | None = None) -> None:
        """Initialize the generator."""
        else_ = [] if else_ is None else else_
        super().__init__(then_, else_=else_)

    @override
    def _condition(self, record: Record, **kwargs: Any) -> bool:
        if getattr(record, "is_draft", False):
            return False
        records_service = current_runtime.get_record_service_for_record(record)
        try:
            records_service.config.draft_cls.pid.resolve(record["id"])  # by edit - has the same id as parent record
            # I'm not sure what open unpublished means
        except NoResultFound:
            return True
        else:
            return False
