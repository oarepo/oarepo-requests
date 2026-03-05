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
from typing import Any, cast, override

from invenio_access.permissions import system_user_id
from invenio_notifications.registry import EntityResolverRegistry
from invenio_records_resources.references import EntityResolver
from invenio_records_resources.references.entity_resolvers import (
    EntityProxy,
    ServiceResultProxy,
    ServiceResultResolver,
)
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_users_resources.entity_resolvers import UserProxy
from oarepo_workflows.resolvers.multiple_entities import (
    MultipleEntitiesProxy,
    MultipleEntitiesResolver,
)


class UserNotificationProxy(ServiceResultProxy):
    """Entity proxy for user notifications."""

    system_record = UserProxy.system_record
    ghost_record = UserProxy.ghost_record

    def _resolve(self) -> dict[str, Any]:
        """Resolve the User from the proxy's reference dict, or system_identity."""
        user_id = self._parse_ref_dict_id()
        if user_id == system_user_id:  # system_user_id is a string: "system"
            return self.system_record()  # type: ignore[no-any-return]
        try:
            return super()._resolve()  # type: ignore[no-any-return]
        except PermissionDeniedError:
            return self.ghost_record({"id": user_id})  # type: ignore[no-any-return]


class MultipleEntitiesNotificationProxy(EntityProxy):
    """Entity proxy for email addresses."""

    # not used in notifications but required for inheritance
    get_needs = MultipleEntitiesProxy.get_needs
    pick_resolved_fields = MultipleEntitiesProxy.pick_resolved_fields

    @override
    def _resolve(self) -> list[dict[str, dict[str, Any]]]:  # type: ignore[reportIncompatibleMethodOverride]
        """Resolve the User from the proxy's reference dict, or system_identity."""
        entity_refs = json.loads(self._parse_ref_dict_id())

        fields: list[dict[str, dict[str, Any]]] = []
        for entity_ref in entity_refs:
            type_ = next(iter(entity_ref.keys()))
            fields.append(
                {
                    type_: cast(
                        "dict[str, Any]",
                        EntityResolverRegistry.resolve_entity(entity_ref),
                    )
                }
            )

        return fields


class MultipleEntitiesNotificationResolver(EntityResolver):
    """Resolver for user notifications."""

    type_id = MultipleEntitiesResolver.type_id
    matches_reference_dict = MultipleEntitiesResolver.matches_reference_dict
    matches_entity = MultipleEntitiesResolver.matches_entity
    _reference_entity = MultipleEntitiesResolver._reference_entity  # noqa SLF001

    def __init__(self) -> None:
        """Initialize the resolver."""
        super().__init__("multiple")

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> EntityProxy:
        """Return a UserProxy for the given reference dict."""
        return MultipleEntitiesNotificationProxy(self, ref_dict)


def requests_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="requests", type_key="request")


def request_events_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="request_events", type_key="request_event")


def user_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="users", type_key="user", proxy_cls=UserNotificationProxy)


def multiple_entities_resolver() -> MultipleEntitiesNotificationResolver:
    """Return community role notification resolver."""
    return MultipleEntitiesNotificationResolver()


requests_resolver.type_key = "request"  # type: ignore[attr-defined]
request_events_resolver.type_key = "request_event"  # type: ignore[attr-defined]
user_resolver.type_key = "user"  # type: ignore[attr-defined]
multiple_entities_resolver.type_key = MultipleEntitiesNotificationResolver.type_id  # type: ignore[attr-defined]
