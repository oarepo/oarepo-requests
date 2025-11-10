#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration for oarepo-requests to be initialized at invenio_config.module entrypoint."""

from __future__ import annotations

import oarepo_workflows  # noqa
from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS as RDM_NOTIFICATIONS_BUILDERS
from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver

from oarepo_requests.notifications.builders.comment import CommentRequestEventCreateNotificationBuilder
from oarepo_requests.notifications.builders.delete_published_record import (
    DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestDeclineNotificationBuilder,
    DeletePublishedRecordRequestSubmitNotificationBuilder,
)
from oarepo_requests.notifications.builders.publish import (
    PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestDeclineNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder,
)
from oarepo_requests.notifications.generators import (
    GroupEmailRecipient,
    MultipleRecipientsEmailRecipients,
    UserEmailRecipient,
)
from oarepo_requests.notifications.user_notification_resolver import UserNotificationResolver
from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService

REQUESTS_SERVICE_CLASS = OARepoRequestsService
REQUESTS_SERVICE_CONFIG_CLASS = OARepoRequestsServiceConfig
REQUESTS_RESOURCE_CLASS = OARepoRequestsResource
REQUESTS_RESOURCE_CONFIG_CLASS = OARepoRequestsResourceConfig


NOTIFICATION_RECIPIENTS_RESOLVERS = {
    "user": {"email": UserEmailRecipient},
    "group": {"email": GroupEmailRecipient},
    "multiple": {"email": MultipleRecipientsEmailRecipients},
}

NOTIFICATIONS_ENTITY_RESOLVERS = [
    UserNotificationResolver(),
    ServiceResultResolver(service_id="requests", type_key="request"),
    ServiceResultResolver(service_id="request_events", type_key="request_event"),
]

NOTIFICATIONS_BACKENDS = {
    EmailNotificationBackend.id: EmailNotificationBackend(),
}

NOTIFICATIONS_BUILDERS = {
    **RDM_NOTIFICATIONS_BUILDERS,
    DeletePublishedRecordRequestSubmitNotificationBuilder.type: DeletePublishedRecordRequestSubmitNotificationBuilder,
    DeletePublishedRecordRequestAcceptNotificationBuilder.type: DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestDeclineNotificationBuilder.type: DeletePublishedRecordRequestDeclineNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder.type: PublishDraftRequestSubmitNotificationBuilder,
    PublishDraftRequestAcceptNotificationBuilder.type: PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestDeclineNotificationBuilder.type: PublishDraftRequestDeclineNotificationBuilder,
    CommentRequestEventCreateNotificationBuilder.type: CommentRequestEventCreateNotificationBuilder,
}
