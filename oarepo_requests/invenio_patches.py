#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Patches to invenio service to allow for more flexible requests handling."""

from __future__ import annotations

from functools import cached_property, partial
from typing import TYPE_CHECKING, Any, override

from flask_babel import LazyString
from invenio_records_resources.services.records.params import FilterParam
from invenio_records_resources.services.records.params.base import ParamInterpreter
from invenio_requests.resources.requests.config import (
    RequestSearchRequestArgsSchema,
    RequestsResourceConfig,
)
from invenio_requests.services.requests.config import (
    RequestSearchOptions,
    RequestsServiceConfig,
)
from invenio_requests.services.requests.params import IsOpenParam
from invenio_search.engine import dsl
from marshmallow import fields
from opensearch_dsl.query import Bool

from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask.blueprints import BlueprintSetupState
    from flask_principal import Identity
    from flask_resources.serializers.base import BaseSerializer
    from invenio_records_resources.services.records.config import SearchOptions
    from opensearch_dsl.query import Query


class RequestOwnerFilterParam(FilterParam):
    """Filter requests by owner."""

    @override
    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
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
    def factory(cls, param: str | None = None) -> partial[ParamInterpreter]:
        """Create a new filter parameter."""
        return partial(cls, param)

    @override
    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
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
    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
        """Apply the filter to the search."""
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter(
                Bool(must_not=[dsl.Q("term", **{self.field_name: identity.id})])
            )
        return search


class IsClosedParam(IsOpenParam):
    """Get just the closed requests."""

    @override
    def apply(self, identity: Identity, search: Query, params: dict[str, str]) -> Query:
        """Evaluate the is_closed parameter on the search."""
        if params.get("is_closed") is True:
            search = search.filter("term", **{self.field_name: True})
        elif params.get("is_closed") is False:
            search = search.filter("term", **{self.field_name: False})
        return search


class EnhancedRequestSearchOptions(RequestSearchOptions):
    """Searched options enhanced with additional filters."""

    params_interpreters_cls = (
        *RequestSearchOptions.params_interpreters_cls,
        RequestOwnerFilterParam.factory("mine", "created_by.user"),
        RequestNotOwnerFilterParam.factory("assigned", "created_by.user"),
        RequestAllAvailableFilterParam.factory("all"),
        IsClosedParam.factory("is_closed"),
    )


class ExtendedRequestSearchRequestArgsSchema(RequestSearchRequestArgsSchema):
    """Marshmallow schema for the extra filters."""

    mine = fields.Boolean()
    assigned = fields.Boolean()
    all = fields.Boolean()
    is_closed = fields.Boolean()


def override_invenio_requests_config(
    state: BlueprintSetupState, *args: Any, **kwargs: Any
) -> None:  # noqa ARG001
    """Override the invenio requests configuration.

    This function is called from the blueprint setup function as this should be a safe moment
    to monkey patch the invenio requests configuration.
    """
    with state.app.app_context():
        # this monkey patch should be done better (support from invenio)
        RequestsServiceConfig.search = EnhancedRequestSearchOptions
        RequestsResourceConfig.request_search_args = (
            ExtendedRequestSearchRequestArgsSchema
        )
        # add extra links to the requests
        for k, v in OARepoRequestsServiceConfig.links_item.items():
            if k not in RequestsServiceConfig.links_item:
                RequestsServiceConfig.links_item[k] = v

        class LazySerializer:
            def __init__(self, serializer_cls: type[BaseSerializer]) -> None:
                self.serializer_cls = serializer_cls

            @cached_property
            def __instance(self) -> BaseSerializer:
                return self.serializer_cls()

            @property
            def serialize_object_list(self) -> Callable:
                return self.__instance.serialize_object_list

            @property
            def serialize_object(self) -> Callable:
                return self.__instance.serialize_object

        # TODO: patch response handlers

        from invenio_i18n import _
        from invenio_requests.proxies import current_request_type_registry
        from invenio_requests.services.requests.facets import status, type  # noqa A004

        status._value_labels = {  # noqa SLF001
            "submitted": _("Submitted"),
            "expired": _("Expired"),
            "accepted": _("Accepted"),
            "declined": _("Declined"),
            "cancelled": _("Cancelled"),
            "created": _("Created"),
        }
        status._label = _("Request status")  # noqa SLF001

        # add extra request types dynamically
        type._value_labels = {
            rt.type_id: rt.name for rt in iter(current_request_type_registry)
        }  # noqa SLF001
        type._label = _("Type")  # noqa SLF001


# TODO: override_invenio_notifications


def resolve_lazy_strings(data: dict | list | LazyString | str) -> str:
    """Resolve lazy strings in the given data."""
    if isinstance(data, dict):
        return {key: resolve_lazy_strings(value) for key, value in data.items()}
    if isinstance(data, list):
        return [resolve_lazy_strings(item) for item in data]
    if isinstance(data, LazyString):
        return str(data)
    return data
