from ..utils import get_matching_service_for_record
from .generic import OARepoAcceptAction

"""
class DeleteTopicAcceptAction(actions.AcceptAction):
    log_event = True

    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        topic_service = get_matching_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        # uow.register(RecordDeleteOp(topic, topic_service.indexer, index_refresh=True))
        topic_service.delete(identity, topic["id"], uow=uow, *args, **kwargs)
        super().execute(identity, uow)
        
"""


def delete_topic(action_obj, identity, uow, *args, **kwargs):
    topic = action_obj.request.topic.resolve()
    topic_service = get_matching_service_for_record(topic)
    if not topic_service:
        raise KeyError(f"topic {topic} service not found")
    topic_service.delete(identity, topic["id"], uow=uow, *args, **kwargs)


class DeleteTopicAcceptAction(OARepoAcceptAction):
    user_execute = delete_topic
