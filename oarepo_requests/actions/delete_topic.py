from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.uow import RecordCommitOp, RecordDeleteOp
from invenio_requests.customizations import SubmitAction
from invenio_requests.resolvers.registry import ResolverRegistry


class DeleteTopicSubmitAction(SubmitAction):
    def execute(self, identity, uow):
        topic = self.request.topic.resolve()
        for resolver in ResolverRegistry.get_registered_resolvers():
            if resolver.matches_entity(topic):
                topic_service = current_service_registry.get(resolver._service_id)
                break
        else:
            raise KeyError(f"topic {topic} service not found")
        uow.register(RecordDeleteOp(topic, topic_service.indexer, index_refresh=True))
        #topic_service.delete(identity, id_, revision_id=None, uow=None)
        super().execute(identity, uow)