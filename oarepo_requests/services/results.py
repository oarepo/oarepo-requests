
from invenio_requests.proxies import current_requests_service
from invenio_requests.services.requests.links import RequestLinksTemplate
from oarepo_runtime.services.results import RecordItem, RecordList

from oarepo_requests.utils import allowed_request_types_for_record_cls, get_request_from_record, \
    get_requests_from_record, get_post_request_url
from invenio_records_resources.services.base.links import Link, LinksTemplate


class RequestLink(Link):
    """Shortcut for writing request links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        # TODO this uses the UUID of the record, should we maybe use the number/ext-id?
        vars.update({"id": record.id})

class RequestsMixin:
    def _process_request_types(self, identity, projection, record, *args, **kwargs):

        request_types_list = []
        allowed_request_types = allowed_request_types_for_record_cls(type(record))

        for request_name, request_type in allowed_request_types.items():
            if request_type.can_possibly_create(identity, record):
                link = Link(get_post_request_url())
                template = LinksTemplate({"create":link})
                request_type_link = {}
                request_type_link["type"] = request_name
                request_type_link["links"] = {"actions": template.expand(identity, request_type)}
                request_types_list.append(request_type_link)

        if request_types_list:
            projection["request_types"] = request_types_list
    def _process_requests(self, identity, projection, record, *args, **kwargs):
        requests_list = []
        requests = get_requests_from_record(identity, record)
        if requests:
            for request_type in requests:
                requests_proj = {}
                requests_proj["links"] = request_type["links"]
                requests_proj["type"] = request_type["type"]
                requests_list.append(requests_proj)

        if requests_list:
            projection["requests"] = requests_list
    def __process_v2(self, identity, projection, record, *args, **kwargs):
        requests = []
        # expand links for all available actions on the request
        for request_type in self._service.config.request_types:
            request = get_request_from_record(identity, record, request_type)
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

        # request_types = get_allowed_request_types(type(record))
        # for type_name, type in request_types:
        #    if type.can_create(self, data, receiver_dict, creator_dict, topic_dict, *args, **kwargs):
        projection["requests"] = requests
    def _additional_process_requests(self, identity, projection, record, *args, **kwargs):
        self._process_requests(identity, projection, record, *args, **kwargs)
        self._process_request_types(identity, projection, record, *args, **kwargs)


class RequestsAwareRecordItem(RecordItem, RequestsMixin):
    """Requests aware record result."""

"""
class RequestsAwareRecordList(RecordList, RequestsMixin):
"""
