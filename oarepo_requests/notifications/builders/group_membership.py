#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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
