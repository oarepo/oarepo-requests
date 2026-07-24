#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo notifications email module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_notifications.backends.email import EmailNotificationBackend as InvenioEmailNotificationBackend
from invenio_notifications.models import Recipient
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service

if TYPE_CHECKING:
    from invenio_notifications.models import Notification


class EmailNotificationBackend(InvenioEmailNotificationBackend):
    """Email specific notification backend that in case of group sends emails to its members."""

    id = "email"

    def _is_group(self, recipient: Recipient) -> bool:
        email = recipient.data.get("email") or recipient.data.get("email_hidden")
        if email:
            return False

        name = recipient.data.get("name")
        if not name:
            return False
        return "@" not in name

    @override
    def send(self, notification: Notification, recipient: Recipient) -> Any:
        """Mail sending implementation."""
        # Resolve email with proper domain handling for groups
        if not self._is_group(recipient):
            return super().send(notification, recipient)

        name = recipient.data.get("name")
        role = Role.query.filter_by(name=name).first()
        if role is None:
            return None
        user_ids = [user.id for user in role.users]  # CommunityMembersRecipient pattern
        filter_u = dsl.Q("terms", id=list(user_ids))
        users = current_users_service.scan(system_identity, extra_filter=filter_u)
        recipients = [Recipient(data=u) for u in users]
        ret = None  # return value is not used anyway
        for r in recipients:
            ret = super().send(notification, r)
        return ret
