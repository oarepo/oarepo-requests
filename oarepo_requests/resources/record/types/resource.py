from flask import g
from flask_resources import resource_requestctx, response_handler, route
from flask_resources.resources import Resource
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import request_view_args

from oarepo_requests.utils import merge_resource_configs


class RecordRequestTypesResource(ErrorHandlersMixin, Resource):
    def __init__(self, record_requests_config, config, service) -> None:
        """:param config: main record resource config
        :param service:
        :param record_requests_config: config specific for the record request serivce
        """
        record_requests_config.blueprint_name = (
            f"{config.blueprint_name}_applicable_requests"
        )
        actual_config = merge_resource_configs(
            config_to_merge_in=record_requests_config, original_config=config
        )
        super().__init__(actual_config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route(
                "GET",
                routes["list-applicable-requests"],
                self.get_applicable_request_types,
            )
        ]
        return url_rules

    @request_view_args
    @response_handler(many=True)
    def get_applicable_request_types(self):
        """List request types."""
        hits = self.service.get_applicable_request_types(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
        )
        return hits.to_dict(), 200
