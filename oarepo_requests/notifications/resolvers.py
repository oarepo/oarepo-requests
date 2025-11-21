#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-communities).
#
# oarepo-communities is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Notifications entity resolvers."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from invenio_access.permissions import system_identity, system_user_id
from invenio_notifications.registry import EntityResolverRegistry
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
from invenio_users_resources.entity_resolvers import UserProxy, UserResolver
from invenio_users_resources.proxies import current_users_service
from oarepo_workflows.resolvers.multiple_entities import MultipleEntitiesProxy, MultipleEntitiesResolver


class UserNotificationResolver(UserResolver):
    """Resolver for user notifications."""

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> UserNotificationProxy:
        """Return a UserProxy for the given reference dict."""
        return UserNotificationProxy(self, ref_dict)


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
            return current_users_service.read(system_identity, user_id).to_dict()  # type: ignore[no-any-return]
        except:  # noqa E722
            return self.ghost_record({"id": user_id})  # type: ignore[no-any-return]


class MultipleEntitiesNotificationResolver(MultipleEntitiesResolver):
    """Resolver for user notifications."""

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> MultipleEntitiesNotificationProxy:
        """Return a UserProxy for the given reference dict."""
        return MultipleEntitiesNotificationProxy(self, ref_dict)


class MultipleEntitiesNotificationProxy(MultipleEntitiesProxy):
    """Proxy for a user entity.

    Supports both system_identity and user_id and returns the user data in dict format required in notifications.
    """

    # Consider whether to reconceptualize inheritance to resolve typing issue
    def _resolve(self) -> dict[str, Any]:  # type: ignore[reportIncompatibleMethodOverride]
        """Resolve the User from the proxy's reference dict, or system_identity."""
        entity_refs = json.loads(self._parse_ref_dict_id())

        fields: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for entity_ref in entity_refs:
            type_ = next(iter(entity_ref.keys()))
            id_ = next(iter(entity_ref.values()))
            fields[type_] |= {id_: EntityResolverRegistry.resolve_entity(entity_ref)}
        return fields


def requests_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="requests", type_key="request")


def request_events_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="request_events", type_key="request_event")


def multiple_entities_resolver() -> MultipleEntitiesNotificationResolver:
    """Return community role notification resolver."""
    return MultipleEntitiesNotificationResolver()


def user_resolver() -> UserNotificationResolver:
    """Return community role notification resolver."""
    return UserNotificationResolver()


requests_resolver.type_key = "request"  # type: ignore[attr-defined]
request_events_resolver.type_key = "request_event"  # type: ignore[attr-defined]
user_resolver.type_key = UserNotificationResolver.type_id  # type: ignore[attr-defined]
multiple_entities_resolver.type_key = MultipleEntitiesNotificationResolver.type_id  # type: ignore[attr-defined]
