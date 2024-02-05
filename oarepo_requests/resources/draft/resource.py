from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference

from oarepo_requests.resources.record.resource import RecordRequestsResource


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
