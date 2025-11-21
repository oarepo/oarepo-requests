#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration of oarepo-requests."""

from __future__ import annotations

from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS as RDM_NOTIFICATIONS_BUILDERS
from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from invenio_users_resources.notifications.generators import UserRecipient
from oarepo_workflows.requests.events import WorkflowEvent

from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestActionComponent,
    WorkflowTransitionComponent,
)
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
from oarepo_requests.notifications.generators import MultipleRecipients

REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

DEFAULT_WORKFLOW_EVENTS = {
    CommentEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
    LogEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
}

REQUESTS_ACTION_COMPONENTS: tuple[type[RequestActionComponent], ...] = (
    WorkflowTransitionComponent,
    AutoAcceptComponent,
)

# TODO: possibly not used outside ui
PUBLISH_REQUEST_TYPES = ["publish_draft", "publish_new_version"]


NOTIFICATION_RECIPIENTS_RESOLVERS = {
    "user": lambda key, notification: UserRecipient(key),  # noqa ARG005
    "multiple": lambda key, notification: MultipleRecipients(key),  # noqa ARG005
}

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
