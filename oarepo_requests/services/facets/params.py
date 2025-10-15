#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo requests facets param interpreters."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, override

from invenio_records_resources.services.records.params import (
    FilterParam,
    ParamInterpreter,
)
from invenio_requests.services.requests.params import IsOpenParam
from invenio_search.engine import dsl

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.services import SearchOptions
    from invenio_search.api import RecordsSearchV2


class RequestOwnerFilterParam(FilterParam):
    """Filter requests by owner."""

    @override
    def apply(self, identity: Identity, search: RecordsSearchV2, params: dict[str, str]) -> RecordsSearchV2:  # type: ignore[reportIncompatibleMethodOverride]
        """Apply the filter to the search."""
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter("term", **{self.field_name: identity.id})
        return search


class RequestAllAvailableFilterParam(ParamInterpreter):
    """A no-op filter that returns all requests that are readable by the current user."""

    def __init__(self, param_name: str, config: type[SearchOptions]) -> None:
        """Initialize the filter."""
        self.param_name = param_name
        super().__init__(config)

    @classmethod
    def factory(cls, param: str) -> partial[ParamInterpreter]:
        """Create a new filter parameter."""
        return partial(cls, param)

    @override
    def apply(self, identity: Identity, search: RecordsSearchV2, params: dict[str, str]) -> RecordsSearchV2:  # type: ignore[reportIncompatibleMethodOverride]
        """Apply the filter to the search - does nothing."""
        params.pop(self.param_name, None)
        return search


class RequestNotOwnerFilterParam(FilterParam):
    """Filter requests that are not owned by the current user.

    Note: invenio still does check that the user has the right to see the request,
    so this is just a filter to narrow down the search to requests, that the user
    can approve.
    """

    @override
    def apply(self, identity: Identity, search: RecordsSearchV2, params: dict[str, str]) -> RecordsSearchV2:  # type: ignore[reportIncompatibleMethodOverride]
        """Apply the filter to the search."""
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter(dsl.query.Bool(must_not=[dsl.Q("term", **{self.field_name: identity.id})]))
        return search


class IsClosedParam(IsOpenParam):
    """Get just the closed requests."""

    @override
    def apply(self, identity: Identity, search: RecordsSearchV2, params: dict[str, str]) -> RecordsSearchV2:  # type: ignore[reportIncompatibleMethodOverride]
        """Evaluate the is_closed parameter on the search."""
        if params.get("is_closed") is True:
            search = search.filter("term", **{self.field_name: True})
        elif params.get("is_closed") is False:
            search = search.filter("term", **{self.field_name: False})
        return search
