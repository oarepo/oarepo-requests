from functools import cached_property

from invenio_access.permissions import system_identity
from invenio_requests import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)
from invenio_requests.customizations import actions
from invenio_requests.records.api import Request
from invenio_requests.resolvers.registry import ResolverRegistry

from oarepo_requests.proxies import current_oarepo_requests

from ..utils import _reference_query_term


class OARepoGenericActionMixin:
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        pass

    def _execute_with_components(
        self, components, identity, request_type, topic, uow, *args, **kwargs
    ):
        if not components:
            self.apply(identity, request_type, topic, uow, *args, **kwargs)
            super().execute(identity, uow, *args, **kwargs)
        else:
            with components[0].apply(
                identity, request_type, self, topic, uow, *args, **kwargs
            ):
                self._execute_with_components(
                    components[1:], identity, request_type, topic, uow, *args, **kwargs
                )

    @cached_property
    def components(self):
        return [
            component_cls()
            for component_cls in current_oarepo_requests.action_components(self)
        ]

    def execute(self, identity, uow, *args, **kwargs):
        request_type = self.request.type
        topic = self.request.topic.resolve()
        self._execute_with_components(
            self.components, identity, request_type, topic, uow, *args, **kwargs
        )


class AddTopicLinksOnPayloadMixin:
    self_link = None
    self_html_link = None

    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_dict = topic.to_dict()

        if "payload" not in self.request:
            self.request["payload"] = {}

        # invenio does not allow non-string values in the payload, so using colon notation here
        # client will need to handle this and convert to links structure
        # can not use dot notation as marshmallow tries to be too smart and does not serialize dotted keys
        self.request["payload"][self.self_link] = topic_dict["links"]["self"]
        self.request["payload"][self.self_html_link] = topic_dict["links"]["self_html"]
        return topic._record


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    """"""


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    """"""


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    """"""


def _str_from_ref(ref):  # todo look on grants
    # grants are based on needs; idk whether that makes sense here
    return f"{list(ref.keys())[0]}:{list(ref.values())[0]}"


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
