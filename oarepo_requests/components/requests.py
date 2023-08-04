import functools

from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import LogEventType

from oarepo_requests.utils.utils import get_allowed_request_types
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_requests.proxies import current_requests_service, current_request_type_registry, current_events_service


class AllowedRequestsComponent:
    """Service component which sets all data in the record."""

    def before_ui_detail(self, identity, data=None, record=None, errors=None, **kwargs):
        record_cls = kwargs["record_cls"]
        extra_context = kwargs["extra_context"]
        allowed_request_types = get_allowed_request_types(record_cls)
        extra_context["allowed_requests"] = allowed_request_types

class PublishDraftComponentPrivate(ServiceComponent):
    """Service component for request integration."""
    def __init__(self, publish_request_type, delete_request_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publish_request_type = publish_request_type
        self.delete_request_type = delete_request_type

    def create(self, identity, data=None, record=None, **kwargs):
        """Create the review if requested."""
        # topic and request_type in kwargs
        if self.publish_request_type:
            type_ = current_request_type_registry.lookup(self.publish_request_type, quiet=True)
            request_item = current_requests_service.create(identity, {}, type_, receiver=None, topic=record)
            setattr(record.parent, self.publish_request_type, request_item._request)
            self.uow.register(RecordCommitOp(record.parent))
    def publish(self, identity, data=None, record=None, **kwargs):
        publish_request = getattr(record.parent, self.publish_request_type)

        if publish_request is not None:
            request = publish_request.get_object()
            request_status = "accepted"
            request.status = request_status
            setattr(record.parent, self.publish_request_type, None)
            event = LogEventType(payload={"event": request_status, "content": "request was published through direct call without request"})
            _data = dict(payload=event.payload)
            current_events_service.create(
                identity, request.id, _data, event, uow=self.uow
            )

        if self.delete_request_type:
            type_ = current_request_type_registry.lookup(self.delete_request_type, quiet=True)
            request_item = current_requests_service.create(identity, {}, type_, receiver=None, topic=record)
            setattr(record.parent, self.delete_request_type, request_item._request)
            self.uow.register(RecordCommitOp(record.parent))

def PublishDraftComponent(publish_request_type, delete_request_type):
    return functools.partial(PublishDraftComponentPrivate, publish_request_type, delete_request_type)


"""
class DeleteTopicComponent(ServiceComponent):
    def create(self, identity, data=None, record=None, **kwargs):
"""
