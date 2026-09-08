#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo notification builders for publish draft notifications."""

from __future__ import annotations

from ..generators import EntityRecipientGenerator
from .base import RequestActionNotificationBuilder


class PublishDraftRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for publish draft request submit event."""

    type = "publish-draft-request-event.submit"

    recipients = (EntityRecipientGenerator(key="request.receiver"),)  # email only


class PublishDraftRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for publish draft request accept event."""

    type = "publish-draft-request-event.accept"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)


class PublishDraftRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    """Notification builder for publish draft request decline event."""

    type = "publish-draft-request-event.decline"

    recipients = (EntityRecipientGenerator(key="request.created_by"),)


class PublishChangedMetadataRequestSubmitNotificationBuilder(PublishDraftRequestSubmitNotificationBuilder):
    """Notification builder for publish draft request submit event."""

    type = "publish-changed-metadata-request-event.submit"


class PublishChangedMetadataRequestAcceptNotificationBuilder(PublishDraftRequestAcceptNotificationBuilder):
    """Notification builder for publish draft request accept event."""

    type = "publish-changed-metadata-request-event.accept"


class PublishChangedMetadataRequestDeclineNotificationBuilder(PublishDraftRequestDeclineNotificationBuilder):
    """Notification builder for publish draft request decline event."""

    type = "publish-changed-metadata-request-event.decline"


class PublishNewVersionRequestSubmitNotificationBuilder(PublishDraftRequestSubmitNotificationBuilder):
    """Notification builder for publish draft request submit event."""

    type = "publish-new-version-request-event.submit"


class PublishNewVersionRequestAcceptNotificationBuilder(PublishDraftRequestAcceptNotificationBuilder):
    """Notification builder for publish draft request accept event."""

    type = "publish-new-version-request-event.accept"


class PublishNewVersionRequestDeclineNotificationBuilder(PublishDraftRequestDeclineNotificationBuilder):
    """Notification builder for publish draft request decline event."""

    type = "publish-new-version-request-event.decline"
