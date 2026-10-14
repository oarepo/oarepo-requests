# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Filters for notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_notifications.services.filters import RecipientFilter

if TYPE_CHECKING:
    from invenio_notifications.models import Notification, Recipient


class UsersWithNoMailRecipientFilter(RecipientFilter):
    """Recipient filter for filtering system user."""

    def __call__(
        self,
        notification: Notification,  # noqa: ARG002
        recipients: dict[str, Recipient],
    ):
        """Filter system recipient."""
        return {id_: recipient for id_, recipient in recipients.items() if "email" in recipient.data}


class SystemUserRecipientFilter(RecipientFilter):
    """Recipient filter for filtering system user."""

    def __call__(
        self,
        notification: Notification,  # noqa: ARG002
        recipients: dict[str, Recipient],
    ):
        """Filter system recipient."""
        recipients.pop("system", None)
        return recipients
