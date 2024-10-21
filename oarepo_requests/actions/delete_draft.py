from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .cascade_events import cancel_requests_on_topic_delete
from .generic import OARepoAcceptAction


class DeleteDraftAcceptAction(OARepoAcceptAction):
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        cancel_requests_on_topic_delete(
            self.request, topic, uow
        )  # it's ok to cancel the request before actually deleting the topic due to the uow pattern, right?
        topic_service.delete_draft(identity, topic["id"], uow=uow, *args, **kwargs)
