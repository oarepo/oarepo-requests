from oarepo_requests.services.record.types.service import RecordRequestTypesService


class DraftRecordRequestTypesService(RecordRequestTypesService):
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.record_service.config.draft_cls

    def get_applicable_request_types_for_draft(self, identity, record_id):
        record = self.draft_cls.pid.resolve(record_id, registered_only=False)
        return self._get_applicable_request_types(identity, record)
