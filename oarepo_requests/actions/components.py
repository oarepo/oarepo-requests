#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request action components."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, override

from invenio_requests.customizations import RequestActions
from invenio_requests.errors import CannotExecuteActionError

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_records_resources.records import Record
    from invenio_requests.records.api import Request

    from .generic import OARepoGenericActionMixin

log = logging.getLogger(__name__)


class RequestActionComponent:
    """Abstract request action component.

    Implementation warning: calling actions reloading and recommiting request or topic (eg. topic publish) within
    components may cause incorrect behavior due to the fact that changes on the new (reloaded) instance do not
    propagate to commit ops in the stack below."""

    def create(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the create action.

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
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the submit action.

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
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the accept action.

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
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the decline action.

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
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the cancel action.

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
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the component on the expire action.

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

    def _workflow_transition(
        self, identity: Identity, request: Request, topic: Record, action: OARepoGenericActionMixin, uow: UnitOfWork
    ) -> None:
        from oarepo_workflows.proxies import current_oarepo_workflows

        transitions = current_oarepo_workflows.get_workflow(topic).requests()[request.type.type_id].transitions
        target_state = transitions[action.status_to]
        if target_state and not topic.is_deleted:
            current_oarepo_workflows.set_state(
                identity,
                topic,
                target_state,
                request=request,
                uow=uow,
            )

    @override
    def create(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)

    @override
    def submit(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)

    @override
    def accept(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)

    @override
    def decline(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)

    @override
    def cancel(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)

    @override
    def expire(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._workflow_transition(identity, request, topic, action, uow)


class AutoAcceptComponent(RequestActionComponent):
    """A component that auto-accepts the request if the receiver has auto-approve enabled.

    IMPORTANT: This component should only be used on the end.
    """

    @override
    def submit(
        self,
        identity: Identity,
        request: Request,
        topic: Record,
        action: OARepoGenericActionMixin,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if request.status != "submitted":
            return
        receiver_ref = request.receiver  # this is <x>proxy, not dict
        if not receiver_ref.reference_dict.get("auto_approve"):
            return

        action_obj = RequestActions.get_action(request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow, *args, **kwargs)
