#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder


class EscalateRequestSubmitNotificationBuilder(OARepoRequestActionNotificationBuilder):
    type = "escalate-request-event.submit"

    recipients = [EntityRecipient(key="request.receiver")]  # email only
