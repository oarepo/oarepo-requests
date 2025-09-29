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

from invenio_access.permissions import system_identity
from invenio_i18n import _
from invenio_pidstore.errors import PersistentIdentifierError, PIDDoesNotExistError
from invenio_records_resources.records import Record
from invenio_requests.customizations import actions
from invenio_requests.records.api import Request
from oarepo_runtime.proxies import current_runtime

from oarepo_requests.proxies import current_oarepo_requests
from oarepo_requests.utils import reference_entity, ref_to_str

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_records_resources.services.records.results import RecordItem
    from oarepo_requests.actions.components import RequestActionComponent

from invenio_requests.customizations import RequestAction, RequestType

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
    created_topic: Record | None = None

    def __post__init__(self):
        """Assert correct types after initializing."""
        if not isinstance(self.request, Request):
            raise TypeError(
                f"self.request is not instance of Request, got {type(self.request)=}"
            )
        if not isinstance(self.request_type, RequestType):
            raise TypeError(
                f"self.request_type is not instance of Request, got {type(self.request_type)=}"
            )
        if not isinstance(self.topic, Record):
            raise TypeError(
                f"self.topic is not instance of Record, got {type(self.topic)=}"
            )


class OARepoGenericActionMixin:
    """Mixin for all oarepo actions."""

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

    def execute_with_components(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Execute action with components."""
        self._execute_with_components(
            self.components, identity, state, uow, *args, **kwargs
        )

    def _execute_with_components(
        self,
        components: list[RequestActionComponent],
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Execute the action with the given components.

        Each component has an apply method that must return a context manager.
        The context manager is entered and exited in the order of the components
        and the action is executed inside the most inner context manager.
        """
        if not components:
            self.apply(identity, state, uow, *args, **kwargs)
            super().execute(identity, uow, *args, **kwargs)
        else:
            with components[0].apply(identity, state, uow, *args, **kwargs):
                self._execute_with_components(
                    components[1:], identity, state, uow, *args, **kwargs
                )

    @cached_property
    def components(self) -> list[RequestActionComponent]:
        """Return a list of components for this action."""
        return [
            component_cls()
            for component_cls in current_oarepo_requests.action_components(self)
        ]

    def execute(
        self, identity: Identity, uow: UnitOfWork, *args: Any, **kwargs: Any
    ) -> None:
        """Execute the action."""
        request: Request = self.request
        request_type = request.type
        try:
            topic = request.topic.resolve()
        except (PersistentIdentifierError, PIDDoesNotExistError):
            topic = None

        # create a shared state between different actions to track changes in topic/requests etc.
        state: RequestActionState = RequestActionState(
            request=request,
            request_type=request_type,
            topic=topic,
            created_by=request.created_by,
            action=self,
        )

        self._execute_with_components(
            self.components, identity, state, uow, *args, **kwargs
        )


class CreatedTopicMixin:
    """A mixin for action that takes links from the topic and stores them inside the payload."""

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Apply the action to the topic."""
        super().apply(identity, state, uow, *args, **kwargs)
        if not state.created_topic:
            return state.topic
        entity_ref = reference_entity(state.created_topic)
        request: Request = self.request
        if "payload" not in request:
            request["payload"] = {}
        request["payload"]["created_topic"] = ref_to_str(entity_ref)
        return state.topic


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    """Submit action extended for oarepo requests."""

    name = _("Submit")


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    """Decline action extended for oarepo requests."""

    name = _("Decline")


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    """Accept action extended for oarepo requests."""

    name = _("Accept")


class OARepoCancelAction(OARepoGenericActionMixin, actions.CancelAction):
    """Cancel action extended for oarepo requests."""

    name = _("Cancel")

    status_from = ("created", "submitted")
    status_to = "cancelled"
