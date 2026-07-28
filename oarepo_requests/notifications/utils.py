#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Notifications utils."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service

if TYPE_CHECKING:
    from invenio_notifications.models import Recipient
    from invenio_users_resources.services.users.results import UserList


def is_group(recipient: Recipient) -> bool:
    """Check if recipient is a group."""
    email = recipient.data.get("email") or recipient.data.get("email_hidden")
    if email:
        return False

    name = recipient.data.get("name")
    if not name:
        return False
    return "@" not in name


def group_users(name: str) -> UserList:
    """Return users in a group based on group name."""
    role = Role.query.filter_by(name=name).first()
    user_ids = [user.id for user in role.users]  # CommunityMembersRecipient pattern
    filter_u = dsl.Q("terms", id=list(user_ids))
    return current_users_service.scan(system_identity, extra_filter=filter_u)
