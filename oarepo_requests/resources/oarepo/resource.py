from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_headers,
    request_view_args,
)
from invenio_requests.proxies import current_requests_service
from invenio_requests.resources import RequestsResource

from oarepo_requests.utils import stringify_first_val


class OARepoRequestsResource(RequestsResource, ErrorHandlersMixin):

    def __init__(
        self,
        config,
        oarepo_requests_service,
        invenio_requests_service=current_requests_service,
    ):
        # so super methods can be used with original service
        super().__init__(config, invenio_requests_service)
        self.oarepo_requests_service = oarepo_requests_service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        def s(route):
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        base_rules = super().create_url_rules()
        routes = self.config.routes

        url_rules = [
            route("POST", p(routes["list"]), self.create),
            route("POST", p(routes["list-extended"]), self.create_extended),
            route("GET", p(routes["item-extended"]), self.read_extended),
            route("PUT", p(routes["item-extended"]), self.update_extended),
        ]
        return url_rules + base_rules

    @request_extra_args
    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def _update_with_refresh(self):
        item = self.oarepo_requests_service.update(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            data=resource_requestctx.data,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 200

    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def _create(self):

        items = self.oarepo_requests_service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.data.pop("request_type", None),
            topic=(
                stringify_first_val(resource_requestctx.data.pop("topic", None))
                if resource_requestctx.data
                else None
            ),
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_view_args
    @response_handler()
    def read_extended(self):
        """Read an item."""
        item = self.oarepo_requests_service.read(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 200

    def create(self):
        return self._create()

    def create_extended(self):
        return self._create()

    def update(self):
        return self._update_with_refresh()

    def update_extended(self):
        return self._update_with_refresh()
