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

import abc
import contextlib
from typing import TYPE_CHECKING, Any, override
from dataclasses import dataclass

from invenio_requests.customizations import RequestAction, RequestActions, RequestType
from invenio_requests.errors import CannotExecuteActionError

from oarepo_requests.services.permissions.identity import request_active

if TYPE_CHECKING:
    from collections.abc import Generator
    from invenio_drafts_resources.records import Record
    from flask_principal import Identity
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.records.api import Request

    from .generic import OARepoGenericActionMixin

type ActionType = (
    OARepoGenericActionMixin | RequestAction
)  # should be a type intersection, not yet in python


@dataclass
class RequestActionState:
    """RequestActionState dataclass to update possibly changed record between actions steps."""
    
    request: Request
    request_type: RequestType
    topic: Record
    created_by: Any
    action: ActionType
    
    def __post__init__(self):
        """Assert correct types after initializing."""
        assert isinstance(self.request, Request), f"self.request is not instance of Request, got {type(self.request)=}"
        assert isinstance(self.request_type, RequestType), f"self.request_type is not instance of Request, got {type(self.request_type)=}"
        assert isinstance(self.topic, Record), f"self.topic is not instance of Record, got {type(self.topic)=}"
        # assert isinstance(self.action, ActionType), f"self.action is not instance of ActionType, got {type(self.action)=}"
    

class RequestActionComponent(abc.ABC):
    """Abstract request action component."""
    
    @abc.abstractmethod
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> contextlib.AbstractContextManager:
        """Apply the component.

        Must return a context manager

        :param identity: Identity of the user.
        :param request_type: Request type.
        :param action: Action being executed.
        :param topic: Topic of the request.
        :param uow: Unit of work.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """


class RequestIdentityComponent(RequestActionComponent):
    """A component that adds a request active permission to the identity and removes it after processing."""

    @override
    @contextlib.contextmanager
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[None, None, None]:
        identity.provides.add(request_active)
        try:
            yield
        finally:
            if request_active in identity.provides:
                identity.provides.remove(request_active)


class WorkflowTransitionComponent(RequestActionComponent):
    """A component that applies a workflow transition after processing the action.

    When the action is applied, the "status_to" of the request is looked up in
    the workflow transitions for the request and if found, the topic's state is changed
    to the target state.
    """

    @override
    @contextlib.contextmanager
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[None, None, None]:
        from oarepo_workflows.proxies import current_oarepo_workflows
        from sqlalchemy.exc import NoResultFound

        yield
        if (
            not state.topic
        ):  # for example if we are cancelling requests after deleting draft, it does not make sense to attempt changing the state of the draft
            return
        try:
            transitions = (
                current_oarepo_workflows.get_workflow(state.topic)
                .requests()[state.request_type.type_id]
                .transitions
            )
        except (
            NoResultFound
        ):  # parent might be deleted - this is the case for delete_draft request type
            return
        target_state = transitions[state.action.status_to]  # type: ignore
        
        if (
            target_state and not state.topic.is_deleted
        ):  # commit doesn't work on deleted record?
            current_oarepo_workflows.set_state(
                identity,
                state.topic,
                target_state,
                request=state.action.request,  # type: ignore
                uow=uow,
            )


class AutoAcceptComponent(RequestActionComponent):
    """A component that auto-accepts the request if the receiver has auto-approve enabled."""

    @override
    @contextlib.contextmanager
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Generator[None, None, None]:
        yield
        request: Request = state.action.request  # type: ignore
        if request.status != "submitted":
            return
        receiver_ref = state.request.receiver  # this is <x>proxy, not dict
        if not receiver_ref.reference_dict.get("auto_approve"):
            return

        action_obj = RequestActions.get_action(request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow, *args, **kwargs)
