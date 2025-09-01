#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Builders for notifications related to delete published record request."""

from __future__ import annotations

from invenio_notifications.services.generators import EntityResolve

from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder


class DeletePublishedRecordRequestSubmitNotificationBuilder(OARepoRequestActionNotificationBuilder):
    """Notification builder for delete published record request submit action notifications."""

    type = "delete-published-record-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only


class DeletePublishedRecordRequestAcceptNotificationBuilder(OARepoRequestActionNotificationBuilder):
    """Notification builder for delete published record request accept action notifications."""

    type = "delete-published-record-request-event.accept"

    recipients = (EntityRecipient(key="request.created_by"),)

    context = (EntityResolve(key="request"),)


class DeletePublishedRecordRequestDeclineNotificationBuilder(OARepoRequestActionNotificationBuilder):
    """Notification builder for delete published record request decline action notifications."""

    type = "delete-published-record-request-event.decline"

    recipients = (EntityRecipient(key="request.created_by"),)
