
from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference

from oarepo_requests.utils import merge_resource_configs


class RecordRequestsResource(RecordResource):
    def __init__(self, record_requests_config, config, service):
        """
        :param config: main record resource config
        :param service:
        :param record_requests_config: config specific for the record request serivce
        """
        record_requests_config.blueprint_name = f"{config.blueprint_name}_requests"
        actual_config = merge_resource_configs(
            config_to_merge_in=record_requests_config, original_config=config
        )
        super().__init__(actual_config, service)

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route("GET", routes["list-requests"], self.search_requests_for_record),
            route("POST", routes["request-type"], self.create),
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

    @request_extra_args
    @request_view_args
    @request_data
    @response_handler()
    def create(self):
        """Create an item."""
        items = self.service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=resource_requestctx.view_args["request_type"],
            topic_id=resource_requestctx.view_args["pid_value"],
        )

        return items.to_dict(), 201
