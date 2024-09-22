from types import SimpleNamespace

from invenio_records_resources.services import LinksTemplate
from invenio_records_resources.services.base.links import Link

from oarepo_requests.services.results import (
    RequestTypesList,
    allowed_user_request_types,
)
from oarepo_requests.services.schema import RequestTypeSchema


class RecordRequestTypesService:
    def __init__(self, record_service, oarepo_requests_service):
        self.record_service = record_service
        self.oarepo_requests_service = oarepo_requests_service

    # so api doesn't fall apart
    @property
    def config(self):
        return SimpleNamespace(service_id=self.service_id)

    @property
    def service_id(self):
        return f"{self.record_service.config.service_id}_request_types"

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.record_service.config.record_cls

    """
    @property
    def requests_service(self):
        return current_oarepo_requests.requests_service
    """

    def get_applicable_request_types(self, identity, record_id):
        record = self.record_cls.pid.resolve(record_id)
        return self._get_applicable_request_types(identity, record)

    def _get_applicable_request_types(self, identity, record):
        self.record_service.require_permission(identity, "read", record=record)
        allowed_request_types = allowed_user_request_types(identity, record)
        return RequestTypesList(
            service=self.record_service,
            identity=identity,
            results=list(allowed_request_types.values()),
            links_tpl=LinksTemplate(
                {"self": Link("{+record_link_requests}/applicable")}
            ),
            schema=RequestTypeSchema,
            record=record,
        )
