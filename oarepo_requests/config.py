from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestIdentityComponent,
)
from oarepo_requests.types.events.topic_update import TopicUpdateEventType

try:
    import oarepo_workflows  # noqa

    from oarepo_requests.actions.components import WorkflowTransitionComponent
    from oarepo_workflows.requests.events import WorkflowEvent

    workflow_action_components = [WorkflowTransitionComponent]
except ImportError:
    workflow_action_components = []
    WorkflowEvent = None

from oarepo_requests.resolvers.ui import (
    FallbackEntityReferenceUIResolver,
    GroupEntityReferenceUIResolver,
    UserEntityReferenceUIResolver,
)
from oarepo_requests.types import (
    DeletePublishedRecordRequestType,
    EditPublishedRecordRequestType,
    PublishDraftRequestType,
)
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)


REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    PublishDraftRequestType(),
]

REQUESTS_REGISTERED_EVENT_TYPES = [
    TopicUpdateEventType(),
]

REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

if WorkflowEvent:
    DEFAULT_WORKFLOW_EVENT_SUBMITTERS = {
        CommentEventType.type_id: WorkflowEvent(
            submitters=InvenioRequestsPermissionPolicy.can_create_comment
        ),
        LogEventType.type_id: WorkflowEvent(
            submitters=InvenioRequestsPermissionPolicy.can_create_comment
        ),
        TopicUpdateEventType.type_id: WorkflowEvent(
            submitters=InvenioRequestsPermissionPolicy.can_create_comment
        ),
    }
else:
    DEFAULT_WORKFLOW_EVENT_SUBMITTERS = {}


ENTITY_REFERENCE_UI_RESOLVERS = {
    "user": UserEntityReferenceUIResolver("user"),
    "fallback": FallbackEntityReferenceUIResolver("fallback"),
    "group": GroupEntityReferenceUIResolver("group"),
}

REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]

REQUESTS_ACTION_COMPONENTS = {
    "accepted": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "submitted": [
        *workflow_action_components,
        AutoAcceptComponent,
        RequestIdentityComponent,
    ],
    "declined": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "cancelled": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
    "expired": [
        *workflow_action_components,
        RequestIdentityComponent,
    ],
}
