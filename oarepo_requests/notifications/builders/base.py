# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo notification builders base classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, override

from invenio_notifications.backends import EmailNotificationBackend
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import ContextGenerator
from invenio_notifications.services.generators import (
    UserEmailBackend as InvenioUserEmailBackend,
)
from oarepo_runtime.typing import require_kwargs

from oarepo_requests.notifications.filters import (
    SystemUserRecipientFilter,
    UsersWithNoMailRecipientFilter,
)
from oarepo_requests.notifications.generators import ReferenceSavingEntityResolve

if TYPE_CHECKING:
    from invenio_notifications.services.filters import RecipientFilter
    from invenio_requests.records.api import Request


class NotificationBackendWithClassId(Protocol):
    """Protocol for notification backends with class id."""

    backend_id: str


class UserEmailBackend(NotificationBackendWithClassId, InvenioUserEmailBackend):
    """Email backend for user emails."""

    backend_id = EmailNotificationBackend.id


class RequestActionNotificationBuilder(NotificationBuilder):
    """Base class for request action notifications."""

    @classmethod
    @override
    @require_kwargs("request")
    def build(cls, request: Request) -> Notification:
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "backend_ids": [backend.backend_id for backend in cls.recipient_backends],
            },
        )

    context: tuple[ContextGenerator, ...] = (
        ReferenceSavingEntityResolve(key="request"),
        ReferenceSavingEntityResolve(key="request.topic"),
        ReferenceSavingEntityResolve(key="request.created_by"),
        ReferenceSavingEntityResolve(key="request.receiver"),
    )

    recipient_backends: tuple[NotificationBackendWithClassId, ...] = (UserEmailBackend(),)

    recipient_filters: tuple[RecipientFilter, ...] = (
        UsersWithNoMailRecipientFilter(),
        SystemUserRecipientFilter(),
    )
