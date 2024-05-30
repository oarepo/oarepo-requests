from invenio_requests.customizations import actions

from ..utils import get_matching_service_for_record


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
