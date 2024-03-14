from invenio_search.engine import dsl

from oarepo_requests.services.record.service import RecordRequestsService
from oarepo_requests.utils import get_type_id_for_record_cls
from invenio_records_resources.services.uow import unit_of_work

class DraftRecordRequestsService(RecordRequestsService):
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.record_service.config.draft_cls

    # from invenio_rdm_records.services.requests.service.RecordRequestsService
    def search_requests_for_draft(
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
        record = self.draft_cls.pid.resolve(record_id, registered_only=False)
        self.record_service.require_permission(identity, "read_draft", record=record)

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q(
                    "term",
                    **{
                        f"topic.{get_type_id_for_record_cls(self.draft_cls)}": record_id
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


    @unit_of_work()
    def create_for_draft(
            self,
            identity,
            data,
            request_type,
            receiver,
            creator=None,
            topic_id=None,
            expires_at=None,
            uow=None,
            expand=False,
    ):
        record = self.draft_cls.pid.resolve(topic_id, registered_only=False)
        return self.oarepo_requests_service.create(
            identity=identity,
            data=data,
            request_type=request_type,
            receiver=receiver,
            creator=creator,
            topic=record,
            expand=expand,
            uow=uow,
        )
