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


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    """"""


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    """"""


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    """"""
