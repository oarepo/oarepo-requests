from invenio_records_resources.services.base.links import Link, LinksTemplate

from oarepo_requests.resources.config import OARepoRequestsResourceConfig
from oarepo_requests.services.ui_schema import UIRequestTypeSchema
from oarepo_requests.utils import (
    allowed_request_types_for_record_cls,
    get_matching_service_for_record,
    get_requests_service_for_records_service,
)


class RequestTypesComponent:
    def update_data(self, identity, record, projection):
        request_types_list = []
        allowed_request_types = allowed_request_types_for_record_cls(type(record))

        for request_name, request_type in allowed_request_types.items():
            if hasattr(
                request_type, "can_possibly_create"
            ) and request_type.can_possibly_create(identity, record):
                link = Link(f"{{+api}}{OARepoRequestsResourceConfig.url_prefix}")
                template = LinksTemplate({"create": link})

                schema = UIRequestTypeSchema
                data = schema(
                    context={
                        "identity": identity,
                        "record": record,
                    }
                ).dump(
                    request_type,
                )
                # TODO da se tohle dat dovnitr toho schematu?
                data["links"] = {"actions": template.expand(identity, request_type)}

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
        service = get_requests_service_for_records_service(
            get_matching_service_for_record(record)
        )
        if hasattr(record, "is_draft") and record.is_draft:
            requests = list(
                service.search_requests_for_draft(identity, record["id"]).hits
            )
        else:
            requests = list(
                service.search_requests_for_record(identity, record["id"]).hits
            )
        if requests:
            projection["requests"] = requests
