from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.services.results import ResultsComponent, RecordList

from oarepo_requests.services.schema import RequestTypeSchema
from oarepo_requests.utils import (
    allowed_request_types_for_record,
    get_requests_service_for_records_service,
)
from invenio_records_resources.services import LinksTemplate



class RequestTypesComponent(ResultsComponent):
    def update_data(self, identity, record, projection, expand):
        if not expand:
            return
        allowed_request_types = allowed_user_request_types(identity, record)
        request_types_list = serialize_request_types(allowed_request_types, identity, record)
        projection["expanded"]["request_types"] = request_types_list

def allowed_user_request_types(identity, record):
    allowed_request_types = allowed_request_types_for_record(record)
    allowed_request_types = {
        request_type_name: request_type
        for request_type_name, request_type in allowed_request_types.items()
        if hasattr(
            request_type, "can_possibly_create"
        ) and request_type.can_possibly_create(identity, record)
    }
    return allowed_request_types


def serialize_request_types(request_types, identity, record):
    request_types_list = []
    for request_type in request_types.values():
        request_types_list.append(serialize_request_type(request_type, identity, record))
    return request_types_list


def serialize_request_type(request_type, identity, record):
    return RequestTypeSchema(context={"identity": identity, "record": record}).dump(
        request_type
    )


class RequestsComponent(ResultsComponent):
    def update_data(self, identity, record, projection, expand):
        if not expand:
            return

        service = get_requests_service_for_records_service(
            get_record_service_for_record(record)
        )
        reader = (
            service.search_requests_for_draft
            if getattr(record, "is_draft", False)
            else service.search_requests_for_record
        )
        try:
            requests = list(reader(identity, record["id"]).hits)
        except PermissionDeniedError:
            requests = []
        projection["expanded"]["requests"] = requests


class RequestTypesList(RecordList):
    def __init__(self, *args, record=None, **kwargs):
        self._record = record
        super().__init__(*args, **kwargs)

    def to_dict(self):
        """Return result as a dictionary."""
        hits = list(self.hits)

        record_links = self._service.config.links_item
        rendered_record_links = LinksTemplate(record_links, context={}).expand(self._identity, self._record)
        links_tpl = LinksTemplate(
            self._links_tpl._links, context={
            **{
                f'record_link_{k}': v for k, v in rendered_record_links.items()
            }
        })
        res = {
            "hits": {
                "hits": hits,
                "total": self.total,
            }
        }
        if self._links_tpl:
            res["links"] = links_tpl.expand(self._identity, None)

        return res

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Project the record
            projection = self._schema(
                context=dict(
                    identity=self._identity,
                    record=self._record,
                )
            ).dump(
                hit,
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, hit
                )
            yield projection

    @property
    def total(self):
        return len(self._results)