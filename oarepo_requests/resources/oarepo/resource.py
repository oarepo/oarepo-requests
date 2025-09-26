#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo extensions to invenio requests resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_headers,
    request_view_args,
    request_search_args,
)
from invenio_requests.proxies import current_requests_service
from invenio_requests.resources import RequestsResource
from invenio_records_resources.resources.records.utils import search_preference
from oarepo_requests.utils import resolve_reference_dict, stringify_first_val, reference_to_tuple, string_to_reference

if TYPE_CHECKING:
    from invenio_requests.services.requests import RequestsService

    from ...services.oarepo.service import OARepoRequestsService
    from .config import OARepoRequestsResourceConfig


class OARepoRequestsResource(RequestsResource, ErrorHandlersMixin):
    """OARepo extensions to invenio requests resource."""

    def __init__(
        self,
        config: OARepoRequestsResourceConfig,
        oarepo_requests_service: OARepoRequestsService,
        invenio_requests_service: RequestsService = current_requests_service,
    ) -> None:
        """Initialize the service."""
        # so super methods can be used with original service
        super().__init__(config, invenio_requests_service)
        self.oarepo_requests_service = oarepo_requests_service

    def create_url_rules(self) -> list[dict]:
        """Create the URL rules for the record resource."""

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes

        return [
            route("GET", p(routes["list"]), self.search),
            route("POST", p(routes["list"]), self.create),
            route("POST", p(routes["list-args"]), self.create_args),
            route(
                "GET", p(routes["list-applicable"]), self.applicable_request_types
            ),
        ]

    @request_extra_args
    @request_headers
    @request_data
    @response_handler()
    def create(self) -> tuple[dict, int]:
        """Create a new request based on a request type.

        The data is in the form of:
            .. code-block:: json
            {
                "request_type": "request_type",
                "topic": {
                    "type": "pid",
                    "value": "value"
                },
                ...payload
            }
        """

        request_type_id = resource_requestctx.data.pop("request_type", None)
        topic = resolve_reference_dict(string_to_reference(resource_requestctx.data.pop("topic", None)))

        items = self.oarepo_requests_service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=request_type_id,
            topic=topic,
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def create_args(self) -> tuple[dict, int]:
        """Create a new request based on a request type.

        The data is in the form of:
            .. code-block:: json
            {
                "request_type": "request_type",
                "topic": {
                    "type": "pid",
                    "value": "value"
                },
                ...payload
            }
        """
        request_type_id = resource_requestctx.view_args["request_type"]
        topic = resolve_reference_dict(string_to_reference(resource_requestctx.view_args["topic"]))

        items = self.oarepo_requests_service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=request_type_id,
            topic=topic,
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def applicable_request_types(self) -> tuple[dict, int]:
        """List request types."""
        hits = self.service.applicable_request_types(
            identity=g.identity,
            topic=resolve_reference_dict(
                stringify_first_val(resource_requestctx.args["topic"])
            ),
        )
        return hits.to_dict(), 200
