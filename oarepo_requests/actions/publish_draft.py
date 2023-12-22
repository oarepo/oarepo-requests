from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import SubmitAction
from invenio_requests.resolvers.registry import ResolverRegistry

def publish_draft(draft, identity, uow):
    for resolver in ResolverRegistry.get_registered_resolvers():
        if resolver.matches_entity(draft):
            topic_service = current_service_registry.get(resolver._service_id)
            break
    else:
        raise KeyError(f"topic {draft} service not found")
    id_ = draft["id"]

    topic_service.publish(identity, id_, uow=uow, expand=False)


class PublishDraftSubmitAction(SubmitAction):
    def execute(self, identity, uow):
        topic = self.request.topic.resolve()
        setattr(topic.parent, self.request.type.type_id, None)
        uow.register(RecordCommitOp(topic.parent))
        publish_draft(topic, identity, uow)
        super().execute(identity, uow)


"""
class PublishDraftAcceptAction(AcceptAction):
    def execute(self, identity, uow):
        publish_draft(self, identity, uow)
        super().execute(identity, uow)
"""
