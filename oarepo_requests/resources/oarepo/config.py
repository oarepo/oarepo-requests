# ruff: noqa ERA001
# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Config for the extended requests API."""

from __future__ import annotations

from typing import TYPE_CHECKING

import importlib_metadata
import marshmallow as ma
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig

from oarepo_requests.errors import oarepo_requests_error_handlers
from oarepo_requests.services.search import ExtendedRequestSearchRequestArgsSchema

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from http.client import HTTPException

    from flask import Response
    from marshmallow import fields


class OARepoRequestsResourceConfig(RequestsResourceConfig, ConfiguratorMixin):
    """Config for the oarepo requests API."""

    routes = {
        **RequestsResourceConfig.routes,
        "create": "/<topic>/<request_type>",
        "list-applicable": "/applicable",
    }

    request_search_args = ExtendedRequestSearchRequestArgsSchema

    request_view_args = {
        **RequestsResourceConfig.request_view_args,
        "topic": ma.fields.String(),
        "request_type": ma.fields.String(),
    }

    # base is a FromConfig descriptor and entry points must load lazily, so this has to stay a property
    @property
    def error_handlers(  # ty: ignore[invalid-property-type-override]
        self,
    ) -> Mapping[
        type[HTTPException | BaseException] | int,
        Callable[[Exception], Response],
    ]:
        """Get error handlers."""
        error_handlers = dict(super().error_handlers) | oarepo_requests_error_handlers
        for x in importlib_metadata.entry_points(group="oarepo_requests.error_handlers"):
            error_handlers.update(x.load())
        return error_handlers
