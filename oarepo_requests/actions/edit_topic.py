from ..utils import get_matching_service_for_record
from .generic import OARepoAcceptAction


def edit_topic(action_obj, identity, uow, *args, **kwargs):
    topic = action_obj.request.topic.resolve()
    topic_service = get_matching_service_for_record(topic)
    if not topic_service:
        raise KeyError(f"topic {topic} service not found")
    edit_ret = topic_service.edit(identity, topic["id"], uow=uow)
    return edit_ret


class EditTopicAcceptAction(OARepoAcceptAction):
    user_execute = edit_topic
