#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Builders for notifications related to publish draft request."""

from __future__ import annotations

from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder


class PublishDraftRequestSubmitNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    """Notification builder for publish request submit action notifications."""

    type = "publish-draft-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only


class PublishDraftRequestAcceptNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    """Notification builder for publish request accept action notifications."""

    type = "publish-draft-request-event.accept"

    recipients = (EntityRecipient(key="request.created_by"),)


class PublishDraftRequestDeclineNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    """Notification builder for publish request decline action notifications."""

    type = "publish-draft-request-event.decline"

    recipients = (EntityRecipient(key="request.created_by"),)
