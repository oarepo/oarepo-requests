#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Mixin for all oarepo actions."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from invenio_i18n import _
from invenio_requests.customizations import actions

from oarepo_requests.proxies import current_oarepo_requests
from oarepo_requests.services.permissions.identity import request_active

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestAction
    from invenio_requests.records.api import Request

    from oarepo_requests.actions.components import RequestActionComponent
else:
    RequestAction = object


class OARepoGenericActionMixin(RequestAction):
    """Mixin for all oarepo actions."""

    type_id: str
    name: str
    snapshot: bool = False

    def __init__(self, request: Request):
        """Initialize the action."""
        super().__init__(request)
        self._topic = request.topic.resolve()

    @property
    def topic(self) -> Record:
        """Get the topic."""
        return self._topic

    @topic.setter
    def topic(self, value: Record) -> None:
        """Set the topic."""
        self._topic = value

    @property
    def request(self) -> Request:
        """Get the request."""
        return self._request

    @request.setter
    def request(self, value: Request) -> None:  # type: ignore[reportIncompatibleVariableOverride]
        """Set the topic."""
        self._request = value

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

    def execute(self, identity: Identity, uow: UnitOfWork, *args: Any, **kwargs: Any) -> None:
        """Execute the action."""
        was_request_active = request_active in identity.provides
        if not was_request_active:
            identity.provides.add(request_active)
        try:
            self.apply(identity, uow, *args, **kwargs)  # execute the action itself
            super().execute(identity, uow, *args, **kwargs)
            for component in self.components:
                if hasattr(component, self.type_id):
                    getattr(component, self.type_id)(identity, self, uow, *args, **kwargs)
        finally:
            # in case we are not running the actions in isolated state
            if not was_request_active:
                identity.provides.remove(request_active)


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):  # type: ignore[reportIncompatibleVariableOverride]
    """Submit action extended for oarepo requests."""

    type_id = "submit"
    name = _("Submit")


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):  # type: ignore[reportIncompatibleVariableOverride]
    """Decline action extended for oarepo requests."""

    type_id = "decline"
    name = _("Decline")


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):  # type: ignore[reportIncompatibleVariableOverride]
    """Accept action extended for oarepo requests."""

    type_id = "accept"
    name = _("Accept")


class OARepoCancelAction(OARepoGenericActionMixin, actions.CancelAction):  # type: ignore[reportIncompatibleVariableOverride]
    """Cancel action extended for oarepo requests."""

    type_id = "cancel"
    name = _("Cancel")

    status_from = ("created", "submitted")  # type: ignore[reportAssignmentType]
    status_to = "cancelled"
