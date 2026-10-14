# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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
