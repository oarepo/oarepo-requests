#
# This file is part of Invenio.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Notifications is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Notification manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from flask import current_app
from flask_babel import LazyString, force_locale
from invenio_i18n.proxies import current_i18n
from invenio_notifications.manager import NotificationManager as InvenioNotificationManager
from invenio_notifications.models import Notification, Recipient
from invenio_notifications.tasks import dispatch_notification

from oarepo_requests.notifications.utils import group_users, is_group

if TYPE_CHECKING:
    from oarepo_requests.utils import JsonValue


def get_locale(recipient: Recipient) -> str:
    """Get the locale the notification should be resolved in."""
    locale = recipient.data.get("preferences", {}).get("locale")
    if not current_i18n.is_locale_available(locale):
        return cast("str", current_app.config.get("BABEL_DEFAULT_LOCALE", "en"))
    return cast("str", locale)


def resolve_lazy_strings(data: JsonValue) -> JsonValue:
    """Resolve lazy strings in recipient data."""
    if isinstance(data, dict):
        return {key: resolve_lazy_strings(value) for key, value in data.items()}
    if isinstance(data, list):
        return [resolve_lazy_strings(item) for item in data]
    if isinstance(data, LazyString):
        return str(data)
    return data


def expand_recipients(recipients: dict[str, Recipient]) -> dict[str, Recipient]:
    """Expand notification recipients."""
    for k in list(recipients):
        recipient = recipients[k]
        if is_group(recipient):
            del recipients[k]
            recipients.update({u["id"]: Recipient(data=u) for u in group_users(recipient.data["name"])})
    return recipients


class NotificationManager(InvenioNotificationManager):
    """Notification manager.

    Taking care of building notifications and forwarding them to the backend(s).
    """

    # Consumer
    def handle_broadcast(self, notification: Notification) -> None:
        """Handle a notification broadcast."""
        builder = self.builders[notification.type]
        # Resolve and expand entities
        builder.resolve_context(notification)
        # Generate recipients
        recipients = builder.build_recipients(notification)
        recipients = expand_recipients(recipients)
        recipients = builder.filter_recipients(notification, recipients)
        context = notification.context
        for recipient in recipients.values():
            # lazy strings have to be resolved before the <x>.dumps() serialization later
            locale = get_locale(recipient)
            with force_locale(locale):
                recipient.data = cast("dict", resolve_lazy_strings(recipient.data))
                notification.context = cast("dict", resolve_lazy_strings(context))
            recipient_backends = builder.build_recipient_backends(notification, recipient)
            for backend in recipient_backends:
                dispatch_notification.delay(
                    backend,
                    recipient.dumps(),
                    notification.dumps(),
                )
