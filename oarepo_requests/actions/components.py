import abc
import contextlib
from typing import Generator

from invenio_requests.customizations import RequestActions
from invenio_requests.errors import CannotExecuteActionError

from oarepo_requests.services.permissions.identity import request_active


class RequestActionComponent:
    @abc.abstractmethod
    def apply(
        self, identity, request_type, action, topic, uow, *args, **kwargs
    ) -> Generator:
        """

        :param action:
        :param identity:
        :param uow:
        :param args:
        :param kwargs:
        :return:
        """


class RequestIdentityComponent(RequestActionComponent):
    @contextlib.contextmanager
    def apply(self, identity, request_type, action, topic, uow, *args, **kwargs):
        identity.provides.add(request_active)
        try:
            yield
        finally:
            if request_active in identity.provides:
                identity.provides.remove(request_active)


class WorkflowTransitionComponent(RequestActionComponent):
    @contextlib.contextmanager
    def apply(self, identity, request_type, action, topic, uow, *args, **kwargs):
        from oarepo_workflows.proxies import current_oarepo_workflows

        yield
        transitions = (
            current_oarepo_workflows.get_workflow(topic)
            .requests()[request_type.type_id]
            .transitions
        )
        target_state = transitions[action.status_to]
        if (
            target_state and not topic.model.is_deleted
        ):  # commit doesn't work on deleted record?
            current_oarepo_workflows.set_state(
                identity,
                topic,
                target_state,
                request=action.request,
                uow=uow,
            )


class AutoAcceptComponent(RequestActionComponent):
    @contextlib.contextmanager
    def apply(self, identity, request_type, action, topic, uow, *args, **kwargs):
        yield
        if action.request.status != "submitted":
            return
        receiver_ref = action.request.receiver  # this is <x>proxy, not dict
        if not receiver_ref.reference_dict.get("auto_approve"):
            return

        action_obj = RequestActions.get_action(action.request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow, *args, **kwargs)
