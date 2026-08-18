#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for group membership request."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from invenio_notifications.services.uow import NotificationOp
from invenio_requests.customizations import CommentEventType
from invenio_requests.proxies import current_events_service

from ..notifications.builders.group_membership import (
    GroupMembershipRequestAcceptNotificationBuilder,
    GroupMembershipRequestDeclineNotificationBuilder,
    GroupMembershipRequestSubmitNotificationBuilder,
)

if TYPE_CHECKING:
    from flask_principal import Identity

from typing import TYPE_CHECKING

from invenio_i18n import _
from invenio_requests.customizations import actions
from invenio_users_resources.proxies import current_users_service

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork


class GroupMembershipAcceptAction(actions.AcceptAction):
    """Accept request for group membership."""

    name = _("Accept group membership")

    @override
    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        group_id = next(iter(self.request["topic"].values()))
        requester_id = next(iter(self.request["created_by"].values()))
        current_users_service.add_group(identity, requester_id, group_id, uow=uow)

        justification = self.request.get("payload", {}).get("justification")
        if justification:
            current_events_service.create(
                identity,
                self.request.id,
                {"payload": {"content": justification}},
                CommentEventType,
                uow=uow,
            )

        uow.register(NotificationOp(GroupMembershipRequestAcceptNotificationBuilder.build(request=self.request)))
        return super().execute(identity, uow)


class GroupMembershipDeclineAction(actions.DeclineAction):
    """Decline request for group membership."""

    name = _("Decline group membership")

    @override
    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        uow.register(NotificationOp(GroupMembershipRequestDeclineNotificationBuilder.build(request=self.request)))
        return super().execute(identity, uow)


class GroupMembershipSubmitAction(actions.SubmitAction):
    """Submit request for group membership."""

    name = _("Submit group membership")

    @override
    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        uow.register(NotificationOp(GroupMembershipRequestSubmitNotificationBuilder.build(request=self.request)))
        return super().execute(identity, uow)
