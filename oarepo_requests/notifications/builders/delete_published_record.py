#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
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
