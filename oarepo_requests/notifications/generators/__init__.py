#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Notification generators in oarepo-requests."""

from __future__ import annotations

from oarepo_requests.notifications.generators.context import (
    ReferenceSavingEntityResolve,
    RequestEntityResolve,
)
from oarepo_requests.notifications.generators.recipients import (
    EntityRecipientGenerator,
    GeneralRequestParticipantsRecipient,
    MultipleRecipients,
)

__all__ = [
    "EntityRecipientGenerator",
    "GeneralRequestParticipantsRecipient",
    "MultipleRecipients",
    "ReferenceSavingEntityResolve",
    "RequestEntityResolve",
]
