from types import SimpleNamespace

from invenio_search.engine import dsl

from oarepo_requests.proxies import current_oarepo_requests
from oarepo_requests.utils import get_type_id_for_record_cls


class RecordRequestsService:
    def __init__(self, record_service):
        self.record_service = record_service

    # so api doesn't fall apart
    @property
    def config(self):
        return SimpleNamespace(service_id=self.service_id)

    @property
    def service_id(self):
        return f"{self.record_service.config.service_id}_requests"

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.record_service.config.record_cls

    @property
    def requests_service(self):
        """Factory for creating a record class."""
        return current_oarepo_requests.requests_service

    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_record(
        self,
        identity,
        record_id,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for record's requests."""
        record = self.record_cls.pid.resolve(record_id)
        self.record_service.require_permission(identity, "read", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q(
                    "term",
                    **{
                        f"topic.{get_type_id_for_record_cls(self.record_cls)}": record_id
                    },
                ),
            ],
        )
        if extra_filter is not None:
            search_filter = search_filter & extra_filter

        return self.requests_service.search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=search_filter,
            **kwargs,
        )
