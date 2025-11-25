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
from typing import TYPE_CHECKING, Any, cast, override

from flask_principal import Identity
from invenio_notifications.registry import EntityResolverRegistry
from invenio_records_resources.references import EntityResolver
from invenio_records_resources.references.entity_resolvers import EntityProxy, ServiceResultProxy, ServiceResultResolver
from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_workflows.resolvers.multiple_entities import (
    MultipleEntitiesEntity,
)

if TYPE_CHECKING:
    from flask_principal import ItemNeed, Need
    from sqlalchemy import Identity


class UserNotificationProxy(ServiceResultProxy):
    """Proxy for a user entity."""

    # possibly an invenio bug
    def _resolve(self) -> dict[str, Any]:
        """Resolve the User from the proxy's reference dict, or system_identity."""
        try:
            return super()._resolve()  # type: ignore[no-any-return]
        except (
            PermissionDeniedError
        ):  # users service raises PermissionDeniedError on missing resource due to security implications
            return {"id": self._parse_ref_dict_id()}


class MultipleEntitiesNotificationProxy(EntityProxy):
    """Entity proxy for email addresses."""

    @override
    def _resolve(self) -> list[dict[str, dict[str, Any]]]:  # type: ignore[reportIncompatibleMethodOverride]
        """Resolve the User from the proxy's reference dict, or system_identity."""
        entity_refs = json.loads(self._parse_ref_dict_id())

        fields: list[dict[str, dict[str, Any]]] = []
        for entity_ref in entity_refs:
            type_ = next(iter(entity_ref.keys()))
            fields.append({type_: EntityResolverRegistry.resolve_entity(entity_ref)})

        return fields

    # not used in notifications but required for inheritance
    @override
    def get_needs(self, ctx: dict | None = None) -> list[Need | ItemNeed]:
        """Get the needs provided by the entity."""
        return []

    @override
    def pick_resolved_fields(self, identity: Identity, resolved_dict: dict[str, Any]) -> dict[str, Any]:
        """Select which fields to return when resolving the reference."""
        return resolved_dict


class MultipleEntitiesNotificationResolver(EntityResolver):
    """Resolver for user notifications."""

    type_id = "multiple"

    def __init__(self) -> None:
        """Initialize the resolver."""
        super().__init__("multiple")

    def _get_entity_proxy(self, ref_dict: dict[str, str]) -> EntityProxy:
        """Return a UserProxy for the given reference dict."""
        return MultipleEntitiesNotificationProxy(self, ref_dict)

    @override
    def matches_reference_dict(self, ref_dict: dict) -> bool:
        """Check if the reference dictionary can be resolved by this resolver."""
        return cast("bool", self._parse_ref_dict_type(ref_dict) == self.type_id)

    @override
    def matches_entity(self, entity: Any) -> bool:
        """Check if the entity can be serialized to a reference by this resolver."""
        return isinstance(entity, MultipleEntitiesEntity)

    @override
    def _reference_entity(self, entity: MultipleEntitiesEntity) -> dict[str, str]:
        """Return a reference dictionary for the entity."""
        return {self.type_id: entity.id}


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
