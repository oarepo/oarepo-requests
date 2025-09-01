#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""General OARepo notification builders related classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from invenio_notifications.backends import EmailNotificationBackend
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend

if TYPE_CHECKING:
    from invenio_requests.records.api import Request


class OARepoUserEmailBackend(UserEmailBackend):
    """OARepo email backend."""

    backend_id = EmailNotificationBackend.id


class OARepoRequestActionNotificationBuilder(NotificationBuilder):
    """General OARepo notification builder."""

    @classmethod
    @override
    def build(cls, request: Request) -> Notification:
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "backend_ids": [backend.backend_id for backend in cls.recipient_backends],
            },
        )

    context = (
        EntityResolve(key="request"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.created_by"),
    )

    recipient_backends = (OARepoUserEmailBackend(),)
