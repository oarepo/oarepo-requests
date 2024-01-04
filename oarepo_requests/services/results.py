
from invenio_requests.proxies import current_requests_service
from invenio_requests.services.requests.links import RequestLinksTemplate
from oarepo_runtime.services.results import RecordItem, RecordList


class RequestsMixin:
    def _process_requests(self, projection, record, *args, **kwargs):
        requests = []
        # expand links for all available actions on the request
        for request_type in self._service.config.request_types:
            request = getattr(record.parent, request_type, None)
            if request is None:
                continue
            requests_template = RequestLinksTemplate(
                self._service.config.requests_links_item,
                self._service.config.requests_action_link,
                context={
                    "permission_policy_cls": current_requests_service.config.permission_policy_cls
                },
            )
            requests_links = requests_template.expand(self._identity, request)
            requests.append({"links": requests_links, "type": request_type})
        projection["requests"] = requests


class RequestsAwareRecordItem(RecordItem, RequestsMixin):
    """Requests aware record result."""


class RequestsAwareRecordList(RecordList, RequestsMixin):
    """List of requests aware records result."""
