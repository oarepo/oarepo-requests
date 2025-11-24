#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo notification builders for escalations notifications."""

from __future__ import annotations

from ..generators import EntityRecipientGenerator
from .base import RequestActionNotificationBuilder


class EscalateRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for escalate request submit event."""

    type = "escalate-request-event.submit"

    recipients = (EntityRecipientGenerator(key="request.receiver"),)
