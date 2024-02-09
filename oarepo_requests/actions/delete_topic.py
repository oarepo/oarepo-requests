from invenio_records_resources.services.uow import RecordDeleteOp

# from .generic import AcceptAction
from invenio_requests.customizations import actions

from ..utils import get_matching_service_for_record


class DeleteTopicAcceptAction(actions.AcceptAction):
    def execute(self, identity, uow):
        topic = self.request.topic.resolve()
        topic_service = get_matching_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        uow.register(RecordDeleteOp(topic, topic_service.indexer, index_refresh=True))
        # topic_service.delete(identity, id_, revision_id=None, uow=None)
        super().execute(identity, uow)
