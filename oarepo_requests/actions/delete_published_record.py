from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import OARepoAcceptAction
from .cascade_events import cancel_requests_on_topic_delete


class DeletePublishedRecordAcceptAction(OARepoAcceptAction):
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        cancel_requests_on_topic_delete(self.request, topic, uow)
        topic_service.delete(identity, topic["id"], uow=uow, *args, **kwargs)
