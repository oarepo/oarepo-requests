#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Builders for notifications related to escalation request."""

from __future__ import annotations

from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder


class EscalateRequestSubmitNotificationBuilder(OARepoRequestActionNotificationBuilder):
    """Notification builder for escalation request submit action events."""

    type = "escalate-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only
