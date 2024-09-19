from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import request_view_args

from oarepo_requests.resources.record.types.resource import (
    ApplicableRecordRequestsResource,
)


class ApplicableDraftRequestsResource(ApplicableRecordRequestsResource):

    def create_url_rules(self):
        old_rules = super().create_url_rules()
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        url_rules = [
            route(
                "GET",
                routes["list-applicable-requests-draft"],
                self.get_applicable_request_types_for_draft,
            )
        ]
        return url_rules + old_rules

    @request_view_args
    @response_handler(many=True)
    def get_applicable_request_types_for_draft(self):
        """List request types."""
        hits = self.service.get_applicable_request_types_for_draft(
            identity=g.identity,
            record_id=resource_requestctx.view_args["pid_value"],
        )
        return hits.to_dict(), 200
