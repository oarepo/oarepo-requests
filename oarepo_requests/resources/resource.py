from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_headers,
    request_view_args, request_search_args,
)

from invenio_requests.resources.requests.resource import RequestsResource
from flask_resources.resources import Resource
from invenio_records_resources.resources.records.resource import RecordResource
from invenio_records_resources.resources.records.utils import search_preference
class RecordRequestsResource(RecordResource):
    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route("GET", routes["list"], self.search_requests_for_record),
        ]
        return url_rules

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_requests_for_record(self):
        """Perform a search over the items."""
        hits = self.service.search_requests_for_record(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

class DraftRecordRequestsResource(RecordRequestsResource):
    def create_url_rules(self):
        old_rules = super().create_url_rules()
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route("GET", routes["list-drafts"], self.search_requests_for_draft),
        ]
        return url_rules + old_rules

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search_requests_for_draft(self):
        """Perform a search over the items."""
        hits = self.service.search_requests_for_draft(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

class OARepoRequestsResource(RequestsResource, ErrorHandlersMixin):
    """
    def __init__(self, config, service):
        super().__init__(config)
        self.service = service
    """
    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        base_routes = super().create_url_rules()
        routes = self.config.routes
        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        def s(route):
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        url_rules = [
            route("POST", p(routes["list"]), self.create),
            route("POST", p(routes["list-extended"]), self.create_extended),
            route("GET", p(routes["item-extended"]), self.read_extended)
        ]
        return url_rules + base_routes

    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def create(self):
        def stringify_first_val(dct):
            if isinstance(dct, dict):
                for k, v in dct.items():
                    dct[k] = str(v)
            return dct

        items = self.service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.data.pop("request_type", None),
            receiver=stringify_first_val(resource_requestctx.data.pop("receiver", None))
            if resource_requestctx.data
            else None,
            creator=stringify_first_val(resource_requestctx.data.pop("creator", None))
            if resource_requestctx.data
            else None,
            topic=stringify_first_val(resource_requestctx.data.pop("topic", None))
            if resource_requestctx.data
            else None,
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def create_extended(self):
        def stringify_first_val(dct):
            if isinstance(dct, dict):
                for k, v in dct.items():
                    dct[k] = str(v)
            return dct

        items = self.service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.data.pop("request_type", None),
            receiver=stringify_first_val(resource_requestctx.data.pop("receiver", None))
            if resource_requestctx.data
            else None,
            creator=stringify_first_val(resource_requestctx.data.pop("creator", None))
            if resource_requestctx.data
            else None,
            topic=stringify_first_val(resource_requestctx.data.pop("topic", None))
            if resource_requestctx.data
            else None,
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

    @request_extra_args
    @request_view_args
    @response_handler()
    def read_extended(self):
        """Read an item."""
        item = self.service.read_extended(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            expand=resource_requestctx.args.get("expand", False),
        )
        return item.to_dict(), 200
