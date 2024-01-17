from invenio_records_resources.services.base.links import Link, LinksTemplate

from oarepo_requests.utils import (
    allowed_request_types_for_record_cls,
    get_post_request_url,
    get_requests_from_record,
)


class RequestTypesComponent:
    def update_data(self, identity, record, projection):
        request_types_list = []
        allowed_request_types = allowed_request_types_for_record_cls(type(record))

        for request_name, request_type in allowed_request_types.items():
            if request_type.can_possibly_create(identity, record):
                link = Link(get_post_request_url())
                template = LinksTemplate({"create": link})
                request_type_link = {}
                request_type_link["type"] = request_name
                request_type_link["links"] = {
                    "actions": template.expand(identity, request_type)
                }
                request_types_list.append(request_type_link)

        if request_types_list:
            projection["request_types"] = request_types_list


class RequestsComponent:
    def update_data(self, identity, record, projection):
        requests = get_requests_from_record(identity, record)
        if requests:
            projection["requests"] = requests
