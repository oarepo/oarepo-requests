# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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


class PublishChangedMetadataSubmitAction(PublishDraftSubmitAction):
    """Submit action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestSubmitNotificationBuilder


class PublishChangedMetadataAcceptAction(PublishDraftAcceptAction):
    """Accept action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestAcceptNotificationBuilder


class PublishChangedMetadataDeclineAction(PublishDraftDeclineAction):
    """Decline action for publishing draft requests."""

    notification_builder = PublishChangedMetadataRequestDeclineNotificationBuilder
