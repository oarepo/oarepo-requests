#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-communities).
#
# oarepo-communities is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Filters for notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_notifications.services.filters import RecipientFilter

if TYPE_CHECKING:
    from invenio_notifications.models import Notification, Recipient


class UsersWithNoMailRecipientFilter(RecipientFilter):
    """Recipient filter for filtering system user."""

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):  # noqa ARG002
        """Filter system recipient."""
        return {id_: recipient for id_, recipient in recipients.items() if "email" in recipient.data}
