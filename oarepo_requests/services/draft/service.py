from invenio_search.engine import dsl

from oarepo_requests.services.record.service import RecordRequestsService
from oarepo_requests.utils import get_type_id_for_record_cls


class DraftRecordRequestsService(RecordRequestsService):
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.config.draft_cls

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
        self.require_permission(identity, "read_draft", record=record)

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
