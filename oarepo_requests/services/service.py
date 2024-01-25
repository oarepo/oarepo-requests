from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.requests.service import RequestsService

from oarepo_requests.errors import UnknownRequestType
from oarepo_requests.services.ui_schema import UIRequestSchema, get_request_ui_schema
from thesis.proxies import current_service
from invenio_search.engine import dsl
from invenio_records_resources.services.base.service import Service

class RecordRequestsService(Service):
    @property
    def record_service(self):
        """Factory for creating a record class."""
        return self.config.record_service

    @property
    def requests_service(self):
        """Factory for creating a record class."""
        return self.config.requests_service


    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_record(
        self,
        identity,
        record_id,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs
    ):
        """Search for record's requests."""
        record = self.record_service.record_cls.pid.resolve(record_id)
        self.record_service.require_permission(identity, "read", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q("term", **{f"topic.thesis": record_id}),
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
            **kwargs
        )

class DraftRecordRequestsService(RecordRequestsService):
    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_draft(
            self,
            identity,
            record_id,
            params=None,
            search_preference=None,
            expand=False,
            extra_filter=None,
            **kwargs
    ):
        """Search for record's requests."""
        record = self.record_service.draft_cls.pid.resolve(record_id, registered_only=False)
        self.record_service.require_permission(identity, "read_draft", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q("term", **{f"topic.thesis_draft": record_id}),
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
            **kwargs
        )


class OARepoRequestsService(RequestsService):


    @unit_of_work()
    def create(
        self,
        identity,
        data,
        request_type,
        receiver,
        creator=None,
        topic=None,
        expires_at=None,
        uow=None,
        expand=False,
    ):
        type_ = current_request_type_registry.lookup(request_type, quiet=True)
        if not type_:
            raise UnknownRequestType(request_type)
        if hasattr(type_, "can_create"):
            error = type_.can_create(identity, data, receiver, topic, creator)
        else:
            error = None
        if not error:
            return super().create(
                identity=identity,
                data=data,
                request_type=type_,
                receiver=receiver,
                creator=creator,
                topic=topic,
                expand=expand,
                uow=uow,
            )

    def read_extended(self, identity, id_, expand=False):
        api_request = super().read(identity, id_, expand)
        return api_request

