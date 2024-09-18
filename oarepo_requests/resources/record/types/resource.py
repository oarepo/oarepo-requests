import copy

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
from flask_resources.resources import Resource

class ApplicableRecordRequestsResource(Resource):
    def __init__(self, record_requests_config, config, service):
        """
        :param config: main record resource config
        :param service:
        :param record_requests_config: config specific for the record request serivce
        """
        actual_config = copy.deepcopy(record_requests_config)
        actual_config.blueprint_name = f"{config.blueprint_name}_requests"
        vars_to_overwrite = [x for x in dir(config) if not x.startswith("_")]
        actual_keys = dir(actual_config)
        for var in vars_to_overwrite:
            if var not in actual_keys:
                setattr(actual_config, var, getattr(config, var))
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

