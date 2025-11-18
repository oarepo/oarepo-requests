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

from invenio_records_resources.references.entity_resolvers import ServiceResultResolver

from oarepo_requests.notifications.user_notification_resolver import UserNotificationResolver


def requests_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="requests", type_key="request")


def request_events_resolver() -> ServiceResultResolver:
    """Return community role notification resolver."""
    return ServiceResultResolver(service_id="request_events", type_key="request_event")


def user_resolver() -> UserNotificationResolver:
    """Return community role notification resolver."""
    return UserNotificationResolver()


requests_resolver.type_key = "request"  # type: ignore[attr-defined]
request_events_resolver.type_key = "request_event"  # type: ignore[attr-defined]
user_resolver.type_key = UserNotificationResolver.type_id  # type: ignore[attr-defined]
