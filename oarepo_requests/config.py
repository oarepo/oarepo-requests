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
import oarepo_workflows  # noqa
from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows.requests.events import WorkflowEvent

from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    CreatedTopicComponent,
    RequestActionComponent,
    WorkflowTransitionComponent,
)
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService
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
    TopicUpdateEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
    TopicDeleteEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
    EscalationEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
    RecordSnapshotEventType.type_id: WorkflowEvent(submitters=InvenioRequestsPermissionPolicy.can_create_comment),
}

REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]

REQUESTS_ACTION_COMPONENTS: tuple[type[RequestActionComponent], ...] = (
    AutoAcceptComponent,
    CreatedTopicComponent,
    WorkflowTransitionComponent,
)

# TODO: notifications config

SNAPSHOT_CLEANUP_DAYS = 365

# TODO: where is this used?
PUBLISH_REQUEST_TYPES = ["publish_draft", "publish_new_version"]


NOTIFICATIONS_BACKENDS = {
    EmailNotificationBackend.id: EmailNotificationBackend(),
}

REQUESTS_SERVICE_CLASS = OARepoRequestsService
REQUESTS_SERVICE_CONFIG_CLASS = OARepoRequestsServiceConfig
