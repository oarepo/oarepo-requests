
from ..utils import get_matching_service_for_record
from .generic import OARepoAcceptAction

"""
def publish_draft(draft, identity, uow, *args, **kwargs):
    topic_service = get_matching_service_for_record(draft)
    if not topic_service:
        raise KeyError(f"topic {draft} service not found")
    id_ = draft["id"]
    return topic_service.publish(identity, id_, uow=uow, expand=False, *args, **kwargs)


class PublishDraftAcceptAction(actions.AcceptAction):
    log_event = True

    def execute(self, identity, uow, *args, **kwargs):
        topic = self.request.topic.resolve()
        record = publish_draft(topic, identity, uow, *args, **kwargs)
        super().execute(identity, uow, *args, **kwargs)
        return record._record



class RequestIdentityPublishDraftAcceptAction(PublishDraftAcceptAction):
    def execute(self, identity, uow, *args, **kwargs):
        identity = RequestIdentity(identity)
        super().execute(
            identity, uow, *args, **kwargs
        )  # the permission is resolved in execute action method of requests service
"""


# ------
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
    action = publish_draft
