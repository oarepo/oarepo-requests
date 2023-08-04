from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.customizations import SubmitAction, AcceptAction
from invenio_requests.resolvers.registry import ResolverRegistry

from oarepo_requests.types.delete_record import DeleteRecordRequestType
from oarepo_requests.utils.utils import get_allowed_request_types

"""
def create_delete_request(topic_service, topic_id, identity):
    record = topic_service.record_cls.pid.resolve(topic_id)
    allowed_types = get_allowed_request_types(type(record))
    type_ = next(x for x in allowed_types.values() if issubclass(x, DeleteRecordRequestType))
    current_requests_service.create(identity=identity, data={}, request_type=type_, receiver=None, topic=record)
"""
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