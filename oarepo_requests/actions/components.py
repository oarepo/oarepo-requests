#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request action components.

These components are called as context managers when an action is executed.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast, override

from invenio_requests.customizations import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from invenio_requests.records.api import Request

from ..utils import ref_to_str, reference_entity
from .generic import OARepoGenericActionMixin, RequestActionState

if TYPE_CHECKING:
    from uuid import UUID

    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork

log = logging.getLogger(__name__)


class RequestActionComponent:
    """Abstract request action component."""

    def create(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the create action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """

    def submit(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the submit action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """

    def accept(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the accept action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """

    def decline(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the decline action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """

    def cancel(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the cancel action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """

    def expire(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the expire action.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """


class WorkflowTransitionComponent(RequestActionComponent):
    """A component that applies a workflow transition after processing the action.

    When the action is applied, the "status_to" of the request is looked up in
    the workflow transitions for the request and if found, the topic's state is changed
    to the target state.
    """

    def _workflow_transition(self, identity: Identity, state: RequestActionState, uow: UnitOfWork) -> None:
        from oarepo_workflows.proxies import current_oarepo_workflows

        transitions = (
            current_oarepo_workflows.get_workflow(state.topic).requests()[state.request_type.type_id].transitions
        )
        target_state = transitions[state.action.status_to]
        if target_state and not state.topic.is_deleted:  # commit doesn't work on deleted record?
            current_oarepo_workflows.set_state(
                identity,
                state.topic,
                target_state,
                request=state.action.request,
                uow=uow,
            )

    @override
    def create(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        self._workflow_transition(identity, state, uow)

    @override
    def submit(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        self._workflow_transition(identity, state, uow)

    @override
    def accept(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        self._workflow_transition(identity, state, uow)

    @override
    def decline(
        self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any
    ) -> None:
        self._workflow_transition(identity, state, uow)

    @override
    def cancel(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        self._workflow_transition(identity, state, uow)

    @override
    def expire(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        self._workflow_transition(identity, state, uow)


class CreatedTopicComponent(RequestActionComponent):
    """A component that saves new topic created within the request on payload."""

    @override
    def accept(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        """Apply the action to the topic."""
        if not state.created_topic:
            return
        entity_ref = reference_entity(state.created_topic)
        request: Request = state.request
        if "payload" not in request:
            request["payload"] = {}
        request["payload"]["created_topic"] = ref_to_str(entity_ref)
        return


class AutoAcceptComponent(RequestActionComponent):
    """A component that auto-accepts the request if the receiver has auto-approve enabled."""

    @override
    def submit(self, identity: Identity, state: RequestActionState, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        request: Request = state.action.request
        if request.status != "submitted":
            return
        receiver_ref = state.request.receiver  # this is <x>proxy, not dict
        if not receiver_ref.reference_dict.get("auto_approve"):
            return

        action_obj = RequestActions.get_action(request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        if isinstance(action_obj, OARepoGenericActionMixin):
            # it is our action, just execute with components right away
            current_action_obj = state.action
            state.action = action_obj
            try:
                action_obj.execute_with_components(*args, identity, state, uow, **kwargs)
            finally:
                state.action = current_action_obj
        else:
            # TODO: consider reconceptualizing this whole RequestActionState thing
            action_obj.execute(identity, uow, *args, **kwargs)
            # we dont know if request/topic was changed, retrieve actual data
            new_request: Request = Request.get_record(cast("UUID", request.id))
            state.request = new_request
            try:
                new_topic = new_request.topic.resolve()
                state.topic = new_topic
            except Exception:
                log.exception("Exception while resolving topic")
