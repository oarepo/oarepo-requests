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

from invenio_notifications.services.generators import EntityResolve

from ..generators import EntityRecipient
from .base import RequestActionNotificationBuilder


class DeletePublishedRecordRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request submit event."""

    type = "delete-published-record-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only


class DeletePublishedRecordRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request accept event."""

    type = "delete-published-record-request-event.accept"

    recipients = (EntityRecipient(key="request.created_by"),)

    context = (EntityResolve(key="request"),)


class DeletePublishedRecordRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for delete published record request decline event."""

    type = "delete-published-record-request-event.decline"

    recipients = (EntityRecipient(key="request.created_by"),)
