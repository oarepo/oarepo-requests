#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from oarepo_requests.actions.publish_draft import (
    PublishDraftAcceptAction,
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)
from oarepo_requests.notifications.builders.publish import (
    PublishChangedMetadataRequestAcceptNotificationBuilder,
    PublishChangedMetadataRequestDeclineNotificationBuilder,
    PublishChangedMetadataRequestSubmitNotificationBuilder,
)


class PublishChangedMetadataSubmitAction(PublishDraftSubmitAction):  # type: ignore[misc]
    """Submit action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestSubmitNotificationBuilder


class PublishChangedMetadataAcceptAction(PublishDraftAcceptAction):  # type: ignore[misc]
    """Accept action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestAcceptNotificationBuilder


class PublishChangedMetadataDeclineAction(PublishDraftDeclineAction):  # type: ignore[misc]
    """Decline action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestDeclineNotificationBuilder
