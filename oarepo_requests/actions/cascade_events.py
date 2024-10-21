from invenio_access.permissions import system_identity
from invenio_requests import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.records import Request
from invenio_requests.resolvers.registry import ResolverRegistry

from oarepo_requests.utils import _reference_query_term


def _str_from_ref(ref):
    k, v = list(ref.items())[0]
    return f"{k}.{v}"


def update_topic(request, old_topic, new_topic, uow):
    from oarepo_requests.types.events import TopicUpdateEventType

    old_topic_ref = ResolverRegistry.reference_entity(old_topic)
    new_topic_ref = ResolverRegistry.reference_entity(new_topic)

    requests_with_topic = current_requests_service.scan(
        system_identity, extra_filter=_reference_query_term("topic", old_topic_ref)
    )
    for request_from_search in requests_with_topic:
        request_type = current_request_type_registry.lookup(
            request_from_search["type"], quiet=True
        )
        if hasattr(request_type, "topic_change"):
            cur_request = (
                Request.get_record(request_from_search["id"])
                if request_from_search["id"] != str(request.id)
                else request
            )  # request on which the action is executed is recommited later, the change must be done on the same instance
            request_type.topic_change(cur_request, new_topic_ref, uow)
            if cur_request.topic.reference_dict != old_topic_ref:
                event = TopicUpdateEventType(
                    payload=dict(
                        old_topic=_str_from_ref(old_topic_ref),
                        new_topic=_str_from_ref(new_topic_ref),
                    )  # event jsonschema requires string
                )
                _data = dict(payload=event.payload)
                current_events_service.create(
                    system_identity, cur_request.id, _data, event, uow=uow
                )


def cancel_requests_on_topic_delete(request, topic, uow):
    from oarepo_requests.types.events import TopicDeleteEventType

    topic_ref = ResolverRegistry.reference_entity(topic)
    requests_with_topic = current_requests_service.scan(
        system_identity, extra_filter=_reference_query_term("topic", topic_ref)
    )
    for request_from_search in requests_with_topic:
        request_type = current_request_type_registry.lookup(
            request_from_search["type"], quiet=True
        )
        if hasattr(request_type, "on_topic_delete"):
            if request_from_search["id"] == str(request.id):
                continue
            cur_request = Request.get_record(request_from_search["id"])
            if cur_request.is_open:
                request_type.on_topic_delete(
                    cur_request, uow
                )  # possibly return message to save on event payload?
                event = TopicDeleteEventType(
                    payload=dict(
                        topic=_str_from_ref(topic_ref),
                    )
                )
                _data = dict(payload=event.payload)
                current_events_service.create(
                    system_identity, cur_request.id, _data, event, uow=uow
                )
