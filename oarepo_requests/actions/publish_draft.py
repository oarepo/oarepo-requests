from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import OARepoAcceptAction


class PublishDraftAcceptAction(OARepoAcceptAction):
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        id_ = topic["id"]
        return topic_service.publish(
            identity, id_, uow=uow, expand=False, *args, **kwargs
        )._record
