#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the extended requests API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import importlib_metadata
import marshmallow as ma
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig
from invenio_requests.resources.requests.config import request_error_handlers

from oarepo_requests.services.search import ExtendedRequestSearchRequestArgsSchema

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_resources import ResponseHandler


class OARepoRequestsResourceConfig(RequestsResourceConfig, ConfiguratorMixin):
    """Config for the extended requests API."""

    blueprint_name = "oarepo_requests"
    url_prefix = "/requests"
    routes: Mapping[str, str] = {
        **RequestsResourceConfig.routes,
        "list": "/",
        "list-args": "/<topic>/<request_type>",
        "list-applicable": "/applicable",
    }

    request_search_args = ExtendedRequestSearchRequestArgsSchema

    # TODO: using stubs - i think dict[str, ma.fields.Field] would fit better here
    # "property" is not assignable to "Mapping[str, Any] ?
    @property
    def request_view_args(self) -> Mapping[str, Any]:  # type: ignore[reportIncompatibleVariableOverride]
        """Request view args for the requests API."""
        # use **
        return cast(
            "dict[str, Any]", super().request_view_args
        ) | {  # TODO: resolve stub has type Mapping but is defined in the superclass as dict
            # ; how this should be typed?
            "topic": ma.fields.String(),
            "request_type": ma.fields.String(),
        }

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:  # type: ignore[reportIncompatibleVariableOverride]
        """Response handlers for the extended requests API."""
        return {
            # TODO: UI serialization
            **super().response_handlers,
        }

    @property
    def error_handlers(self) -> dict[type[Exception], Any]:  # type: ignore[reportIncompatibleVariableOverride]
        """Get error handlers."""
        entrypoint_error_handlers = cast("dict[type[Exception], Any]", request_error_handlers)  # TODO: import correctly

        for x in importlib_metadata.entry_points(group="oarepo_requests.error_handlers"):
            entrypoint_error_handlers.update(x.load())
        for x in importlib_metadata.entry_points(group="oarepo_requests.extended.error_handlers"):
            entrypoint_error_handlers.update(x.load())
        return entrypoint_error_handlers
