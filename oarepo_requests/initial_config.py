#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration for oarepo-requests to be initialized at invenio_config.module entrypoint."""

from __future__ import annotations

import invenio_requests.config
import oarepo_workflows  # noqa
from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS as RDM_NOTIFICATIONS_BUILDERS
from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
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
from oarepo_requests.notifications.builders.delete_published_record import (
    DeletePublishedRecordRequestAcceptNotificationBuilder,
    DeletePublishedRecordRequestDeclineNotificationBuilder,
    DeletePublishedRecordRequestSubmitNotificationBuilder,
)
from oarepo_requests.notifications.builders.escalate import (
    EscalateRequestSubmitNotificationBuilder,
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
from oarepo_requests.resolvers.user_notification_resolver import UserNotificationResolver
from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService
from oarepo_requests.types import (
    DeletePublishedRecordRequestType,
    EditPublishedRecordRequestType,
    PublishDraftRequestType,
)
from oarepo_requests.types.events import TopicDeleteEventType
from oarepo_requests.types.events.escalation import EscalationEventType
from oarepo_requests.types.events.record_snapshot import RecordSnapshotEventType
from oarepo_requests.types.events.topic_update import TopicUpdateEventType
from oarepo_requests.types.new_version import NewVersionRequestType
from oarepo_requests.types.publish_changed_metadata import PublishChangedMetadataRequestType
from oarepo_requests.types.publish_new_version import PublishNewVersionRequestType

REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    NewVersionRequestType(),
    PublishChangedMetadataRequestType(),
    PublishNewVersionRequestType(),
    PublishDraftRequestType(),
]

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

REQUESTS_SERVICE_CLASS = OARepoRequestsService
REQUESTS_SERVICE_CONFIG_CLASS = OARepoRequestsServiceConfig


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
    EscalateRequestSubmitNotificationBuilder.type: EscalateRequestSubmitNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder.type: PublishDraftRequestSubmitNotificationBuilder,
    PublishDraftRequestAcceptNotificationBuilder.type: PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestDeclineNotificationBuilder.type: PublishDraftRequestDeclineNotificationBuilder,
}

REQUESTS_RESOURCE_CLASS = OARepoRequestsResource
REQUESTS_RESOURCE_CONFIG_CLASS = OARepoRequestsResourceConfig
