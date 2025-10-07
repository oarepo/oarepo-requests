#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the extended requests API."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

import importlib_metadata
import marshmallow as ma
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig
from invenio_requests.resources.requests.config import request_error_handlers

from oarepo_requests.services.search import ExtendedRequestSearchRequestArgsSchema

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from http.client import HTTPException

    from flask import Response
    from flask_resources import ResponseHandler
    from marshmallow import fields


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

    @property
    def request_view_args(self) -> Mapping[str, fields.Field]:  # type: ignore[reportIncompatibleVariableOverride]
        """Request view args for the requests API."""
        return {
            **super().request_view_args,
            "topic": ma.fields.String(),
            "request_type": ma.fields.String(),
        }

    @property
    def response_handlers(self) -> Mapping[str, ResponseHandler]:  # type: ignore[reportIncompatibleVariableOverride]
        """Response handlers for the extended requests API."""
        return {
            # TODO: UI serialization
            **super().response_handlers,
        }

    @property
    def error_handlers(  # type: ignore[reportIncompatibleVariableOverride]
        self,
    ) -> Mapping[
        type[HTTPException | BaseException] | int,
        Callable[[Exception], Response],
    ]:
        # I'm sorry It's 11am and i can't remember the point of this
        """Get error handlers."""
        # TODO: lint: this probably isn't ideal; ie request error handlers have different type
        # than error handlers in the stubs
        # TODO: import correctly - use the lazy object pattern
        entrypoint_error_handlers = dict(request_error_handlers)

        for x in importlib_metadata.entry_points(group="oarepo_requests.error_handlers"):
            entrypoint_error_handlers.update(x.load())
        for x in importlib_metadata.entry_points(group="oarepo_requests.extended.error_handlers"):
            entrypoint_error_handlers.update(x.load())
        return MappingProxyType(entrypoint_error_handlers)  # type: ignore[reportReturnType]
