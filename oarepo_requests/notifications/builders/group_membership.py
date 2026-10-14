# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo notification builders for group membership request notifications."""

from __future__ import annotations

from ..generators import EntityRecipientGenerator
from .base import RequestActionNotificationBuilder


class GroupMembershipRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for group membership request submit event."""

    type = "group-membership-request-event.submit"

    recipients = (EntityRecipientGenerator(key="request.receiver"),)  # email only


class GroupMembershipRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for group membership request accept event."""

    type = "group-membership-request-event.accept"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)


class GroupMembershipRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for group membership request decline event."""

    type = "group-membership-request-event.decline"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)
