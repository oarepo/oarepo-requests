# from .generic import AcceptAction
from invenio_requests.customizations import actions

from ..utils import get_matching_service_for_record


class EditTopicAcceptAction(actions.AcceptAction):
    log_event = True

    def execute(self, identity, uow):
        topic = self.request.topic.resolve()
        topic_service = get_matching_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        topic_service.edit(identity, topic.id, uow=uow)
        super().execute(identity, uow)
