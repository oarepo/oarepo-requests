from functools import cached_property

from invenio_requests.customizations import actions

from oarepo_requests.proxies import current_oarepo_requests


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
