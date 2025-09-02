#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Maybe not needed."""

from __future__ import annotations

from invenio_access.permissions import system_identity, system_user_id
from invenio_users_resources.entity_resolvers import UserProxy, UserResolver
from invenio_users_resources.proxies import current_users_service


class UserNotificationProxy(UserProxy):
    """..."""

    # TODO: resolved in new invenio
    # generally look at this resolver-proxy redefinition zoo
    def _resolve(self) -> dict:
        """Resolve the User from the proxy's reference dict, or system_identity."""
        user_id = self._parse_ref_dict_id()
        if user_id == system_user_id:  # system_user_id is a string: "system"
            return self.system_record()
        try:
            return current_users_service.read(system_identity, user_id).data
        except:  # noqa E722
            return self.ghost_record({"id": user_id})


class UserNotificationResolver(UserResolver):
    """..."""

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> UserNotificationProxy:
        """Return a UserProxy for the given reference dict."""
        return UserNotificationProxy(self, ref_dict)
