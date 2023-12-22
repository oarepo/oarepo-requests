
from flask import g
from flask_resources import (
    Resource,
    resource_requestctx,
    response_handler,
    route,
)

from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.resource import (
    request_extra_args,
    request_search_args,
    request_view_args, request_headers, request_data,
)
from invenio_requests import current_requests_service, current_request_type_registry
class OARepoRequestsResource(Resource, ErrorHandlersMixin):

    def __init__(self, config, service=current_requests_service):
        """Constructor."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        url_rules = [
            route("POST", routes["create"], self.create),
        ]
        return url_rules


    @request_extra_args
    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def create(self):
        request_type_str = resource_requestctx.data.get("request_type", None)
        type_ = current_request_type_registry.lookup(
            request_type_str, quiet=True
        )
        def stringify_first_val(dct):
            if isinstance(dct,dict):
                for k, v in dct.items():
                    dct[k] = str(v)
            return dct

        items = self.service.create(
            identity=g.identity,
            data=resource_requestctx.data,
            request_type=type_,
            receiver=stringify_first_val(resource_requestctx.data.get("receiver", None)) if resource_requestctx.data else None,
            creator=stringify_first_val(resource_requestctx.data.get("creator", None)) if resource_requestctx.data else None,
            topic=stringify_first_val(resource_requestctx.data.get("topic", None)) if resource_requestctx.data else None,
            expand=resource_requestctx.args.get("expand", False),
        )

        return items.to_dict(), 201

