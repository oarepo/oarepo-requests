from ..utils import get_matching_service
from invenio_requests.customizations import actions

def publish_draft(draft, identity, uow):
    topic_service = get_matching_service(draft)
    if not topic_service:
        raise KeyError(f"topic {draft} service not found")
    id_ = draft["id"]
    topic_service.publish(identity, id_, uow=uow, expand=False)


class PublishDraftAcceptAction(actions.AcceptAction):
    def execute(self, identity, uow):
        topic = self.request.topic.resolve()
        publish_draft(topic, identity, uow)
        super().execute(identity, uow)
