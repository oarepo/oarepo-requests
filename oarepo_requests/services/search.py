# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo requests search."""

from __future__ import annotations

from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema
from invenio_requests.services.requests.config import RequestSearchOptions
from marshmallow import fields

from oarepo_requests.services.facets.params import (
    IsClosedParam,
    RequestAllAvailableFilterParam,
    RequestNotOwnerFilterParam,
    RequestOwnerFilterParam,
)


class EnhancedRequestSearchOptions(RequestSearchOptions):
    """Searched options enhanced with additional filters."""

    # TODO: params_interpreters_cls: tuple[type[ParamInterpreter], ...]
    #  in stubs is not assignable to partial[ParamInterpreter]
    params_interpreters_cls = (  # type: ignore[reportAssignmentType]
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
