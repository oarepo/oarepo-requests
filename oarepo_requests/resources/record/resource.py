import copy

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference


class RecordRequestsResource(RecordResource):
    def __init__(self, config, service, record_requests_config):
        """
        :param config: main record resource config
        :param service:
        :param record_requests_config: config specific for the record request serivce
        """
        actual_config = copy.deepcopy(config)
        actual_config.blueprint_name = f"{config.blueprint_name}_requests"
        # possibly do some nontrivial merge
        actual_config.routes = record_requests_config.routes
        super().__init__(actual_config, service)

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
