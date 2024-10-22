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


def _get_topic_ref_with_requests(topic):
    topic_ref = ResolverRegistry.reference_entity(topic)
    requests_with_topic = current_requests_service.scan(
        system_identity, extra_filter=_reference_query_term("topic", topic_ref)
    )
    return requests_with_topic, topic_ref


def _create_event(cur_request, payload, event_type, uow):
    data = {"payload": payload}
    current_events_service.create(
        system_identity,
        cur_request.id,
        data,
        event_type=event_type,
        uow=uow,
    )


def update_topic(request, old_topic, new_topic, uow):
    from oarepo_requests.types.events import TopicUpdateEventType

    requests_with_topic, old_topic_ref = _get_topic_ref_with_requests(old_topic)
    new_topic_ref = ResolverRegistry.reference_entity(new_topic)
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
            if (
                cur_request.topic.reference_dict != old_topic_ref
            ):  # what if we don't change topic but still do some event we want to log, ie. cancelling the request because it does not apply to published record
                payload = {
                    "old_topic": _str_from_ref(old_topic_ref),
                    "new_topic": _str_from_ref(new_topic_ref),
                }
                _create_event(cur_request, payload, TopicUpdateEventType, uow)


def cancel_requests_on_topic_delete(request, topic, uow):
    from oarepo_requests.types.events import TopicDeleteEventType

    requests_with_topic, topic_ref = _get_topic_ref_with_requests(topic)
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
                payload = {"topic": _str_from_ref(topic_ref)}
                _create_event(cur_request, payload, TopicDeleteEventType, uow)
