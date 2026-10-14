# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Default configuration of oarepo-requests."""

from __future__ import annotations

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
from oarepo_requests.notifications.generators import MultipleRecipients

# check individual receivers in multiple?
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
    "user": lambda key, _notification: UserRecipient(key),
    "group": lambda key, _notification: UserRecipient(key),
    "multiple": lambda key, _notification: MultipleRecipients(key),
}
NOTIFICATIONS_MANAGER_CLS = "oarepo_requests.notifications.manager.NotificationManager"
