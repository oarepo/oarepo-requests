#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""User entity notification resolver module."""

from __future__ import annotations

from typing import Any

from invenio_access.permissions import system_identity, system_user_id
from invenio_users_resources.entity_resolvers import UserProxy, UserResolver
from invenio_users_resources.proxies import current_users_service


class UserNotificationProxy(UserProxy):
    """Proxy for a user entity.

    Supports both system_identity and user_id and returns the user data in dict format required in notifications.
    """

    def _resolve(self) -> dict[str, Any]:
        """Resolve the User from the proxy's reference dict, or system_identity."""
        user_id = self._parse_ref_dict_id()
        if user_id == system_user_id:  # system_user_id is a string: "system"
            return self.system_record()  # type: ignore[no-any-return]
        try:
            return current_users_service.read(system_identity, user_id).data  # type: ignore[no-any-return]
        except:  # noqa E722
            return self.ghost_record({"id": user_id})  # type: ignore[no-any-return]


class UserNotificationResolver(UserResolver):
    """Resolver for user notifications."""

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> UserNotificationProxy:
        """Return a UserProxy for the given reference dict."""
        return UserNotificationProxy(self, ref_dict)
