# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo notification builders for delete publish request notifications."""

from __future__ import annotations

from ..generators import EntityRecipientGenerator, ReferenceSavingEntityResolve
from .base import RequestActionNotificationBuilder


class DeletePublishedRecordRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request submit event."""

    type = "delete-published-record-request-event.submit"

    recipients = (EntityRecipientGenerator(key="request.receiver"),)  # email only


class DeletePublishedRecordRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request accept event."""

    type = "delete-published-record-request-event.accept"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)

    # topic resolution crashes on RecordDeletedException
    context = (
        ReferenceSavingEntityResolve(key="request"),
        ReferenceSavingEntityResolve(key="request.created_by"),
    )


class DeletePublishedRecordRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request decline event."""

    type = "delete-published-record-request-event.decline"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)
