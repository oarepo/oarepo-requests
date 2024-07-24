from ..utils import get_matching_service_for_record
from .generic import OARepoAcceptAction



class DeleteTopicAcceptAction(OARepoAcceptAction):

    def apply(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        topic_service = get_matching_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        topic_service.delete(identity, topic["id"], uow=uow, *args, **kwargs)
