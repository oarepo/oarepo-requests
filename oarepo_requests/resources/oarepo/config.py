#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the extended requests API."""

from __future__ import annotations

from typing import ClassVar

import importlib_metadata
from flask_resources import ResponseHandler
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig
from invenio_requests.proxies import current_requests_resource
from invenio_requests.resources.requests.config import request_error_handlers
import marshmallow as ma

class OARepoRequestsResourceConfig(RequestsResourceConfig, ConfiguratorMixin):
    """Config for the extended requests API."""

    blueprint_name = "oarepo_requests"
    url_prefix = "/requests"
    routes: ClassVar[dict[str, str]] = {
        **RequestsResourceConfig.routes,
        "list": "/",
        "list-args": "/<topic>/<request_type>",
        # "list-applicable": "/applicable?=<topic>",
        "list-applicable": "/applicable",
    }

    @property
    def request_view_args(self):
        return super().request_view_args | {"topic": ma.fields.String(), "request_type": ma.fields.String()}

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:
        """Response handlers for the extended requests API."""
        return {
            # TODO: UI serialization
            **super().response_handlers,
        }

    @property
    def error_handlers(self) -> dict:
        """Get error handlers."""
        entrypoint_error_handlers = request_error_handlers # TODO: import correctly

        for x in importlib_metadata.entry_points(
            group="oarepo_requests.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        for x in importlib_metadata.entry_points(
            group="oarepo_requests.extended.error_handlers"
        ):
            entrypoint_error_handlers.update(x.load())
        return entrypoint_error_handlers
