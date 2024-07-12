from ..utils import get_matching_service_for_record
from .generic import OARepoAcceptAction

def publish_draft(action_obj, identity, uow, *args, **kwargs):
    topic = action_obj.request.topic.resolve()
    topic_service = get_matching_service_for_record(topic)
    if not topic_service:
        raise KeyError(f"topic {topic} service not found")
    id_ = topic["id"]
    return topic_service.publish(
        identity, id_, uow=uow, expand=False, *args, **kwargs
    )._record


class PublishDraftAcceptAction(OARepoAcceptAction):
    user_execute = publish_draft
