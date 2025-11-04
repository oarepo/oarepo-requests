#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration of oarepo-requests."""

from __future__ import annotations

import invenio_requests.config
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
from oarepo_requests.types.events import TopicDeleteEventType
from oarepo_requests.types.events.escalation import EscalationEventType
from oarepo_requests.types.events.record_snapshot import RecordSnapshotEventType
from oarepo_requests.types.events.topic_update import TopicUpdateEventType

REQUESTS_REGISTERED_EVENT_TYPES = (
    TopicUpdateEventType(),
    TopicDeleteEventType(),
    EscalationEventType(),
    RecordSnapshotEventType(),
    *invenio_requests.config.REQUESTS_REGISTERED_EVENT_TYPES,
)

REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

DEFAULT_WORKFLOW_EVENTS = {
    CommentEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
    LogEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
}

REQUESTS_ACTION_COMPONENTS: tuple[type[RequestActionComponent], ...] = (
    WorkflowTransitionComponent,
    AutoAcceptComponent,
)

SNAPSHOT_CLEANUP_DAYS = 365

# TODO: possibly not used outside ui
PUBLISH_REQUEST_TYPES = ["publish_draft", "publish_new_version"]


NOTIFICATIONS_BACKENDS = {
    EmailNotificationBackend.id: EmailNotificationBackend(),
}
