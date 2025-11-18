#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration of oarepo-requests."""

from __future__ import annotations

from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows.requests.events import WorkflowEvent

from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestActionComponent,
    WorkflowTransitionComponent,
)
from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS as RDM_NOTIFICATIONS_BUILDERS
from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver

from oarepo_requests.notifications.builders.comment import CommentRequestEventCreateNotificationBuilder
from oarepo_requests.notifications.builders.delete_published_record import \
    DeletePublishedRecordRequestSubmitNotificationBuilder, DeletePublishedRecordRequestAcceptNotificationBuilder, \
    DeletePublishedRecordRequestDeclineNotificationBuilder
from oarepo_requests.notifications.builders.publish import PublishDraftRequestSubmitNotificationBuilder, \
    PublishDraftRequestAcceptNotificationBuilder, PublishDraftRequestDeclineNotificationBuilder
from oarepo_requests.notifications.generators import UserEmailRecipient, GroupEmailRecipient, \
    MultipleRecipientsEmailRecipients
from oarepo_requests.notifications.user_notification_resolver import UserNotificationResolver

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
    "user": {"email": UserEmailRecipient},
    "group": {"email": GroupEmailRecipient},
    "multiple": {"email": MultipleRecipientsEmailRecipients},
}

# Can be done through entrypoints
NOTIFICATIONS_ENTITY_RESOLVERS = [
    UserNotificationResolver(),
    ServiceResultResolver(service_id="requests", type_key="request"),
    ServiceResultResolver(service_id="request_events", type_key="request_event"),
]

# has to be reinitialized in finalize_app
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
