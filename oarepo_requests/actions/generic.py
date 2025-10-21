#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Mixin for all oarepo actions."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any

from invenio_i18n import _
from invenio_records_resources.records import Record
from invenio_requests.customizations import actions
from invenio_requests.records.api import Request

from oarepo_requests.proxies import current_oarepo_requests
from oarepo_requests.services.permissions.identity import request_active

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_requests.customizations import RequestAction

    from oarepo_requests.actions.components import RequestActionComponent
else:
    RequestAction = object

from invenio_requests.customizations import RequestType


@dataclass
class RequestActionState:
    """RequestActionState dataclass to update possibly changed record between actions steps."""

    request: Request
    request_type: RequestType
    topic: Record
    created_by: Any
    action: RequestAction
    created_topic: Record | None = None

    def __post__init__(self):
        """Assert correct types after initializing."""
        if not isinstance(self.request, Request):
            raise TypeError(f"self.request is not instance of Request, got {type(self.request)=}")
        if not isinstance(self.request_type, RequestType):
            raise TypeError(f"self.request_type is not instance of Request, got {type(self.request_type)=}")
        if not isinstance(self.topic, Record):
            raise TypeError(f"self.topic is not instance of Record, got {type(self.topic)=}")


class OARepoGenericActionMixin(RequestAction):
    """Mixin for all oarepo actions."""

    type_id: str
    name: str

    @classmethod
    def stateful_name(cls, identity: Identity, **kwargs: Any) -> str | LazyString:  # noqa ARG003
        """Return the name of the action.

        The name can be a lazy multilingual string and may depend on the state of the action,
        request or identity of the caller.
        """
        return cls.name

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the action to the topic."""

    action_components: tuple[type[RequestActionComponent], ...] = ()

    @cached_property
    def components(self) -> list[RequestActionComponent]:
        """Return a list of components for this action."""
        return [component_cls() for component_cls in current_oarepo_requests.action_components()]

    def execute_with_components(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Execute the action with components."""
        self.apply(identity, state, uow, *args, **kwargs)
        super().execute(identity, uow, *args, **kwargs)
        if isinstance(state.action, OARepoGenericActionMixin):
            for component in self.components:
                if hasattr(component, state.action.type_id):
                    # Done like this to avoid breaking API changes.
                    # uow should eventually be passed directly to the component
                    # so service/component method signature matches.
                    getattr(component, state.action.type_id)(identity, state, uow, *args, **kwargs)

    def execute(self, identity: Identity, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        """Execute the action."""
        request: Request = self.request
        request_type = request.type
        topic = request.topic.resolve()
        # create a shared state between different actions to track changes in topic/requests etc.
        state: RequestActionState = RequestActionState(
            request=request,
            request_type=request_type,
            topic=topic,
            created_by=request.created_by,
            action=self,
        )
        identity.provides.add(request_active)
        try:
            self.execute_with_components(
                identity, state, uow, *args, **kwargs
            )  # this can be called only once even in case of cascading actions due to request_active need management
        finally:
            # in case we are not running the actions in isolated state
            identity.provides.remove(request_active)


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    """Submit action extended for oarepo requests."""

    type_id = "submit"
    name = _("Submit")


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    """Decline action extended for oarepo requests."""

    type_id = "decline"
    name = _("Decline")


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    """Accept action extended for oarepo requests."""

    type_id = "accept"
    name = _("Accept")


class OARepoCancelAction(OARepoGenericActionMixin, actions.CancelAction):
    """Cancel action extended for oarepo requests."""

    type_id = "cancel"
    name = _("Cancel")

    status_from = ("created", "submitted")  # type: ignore[reportAssignmentType]
    status_to = "cancelled"
