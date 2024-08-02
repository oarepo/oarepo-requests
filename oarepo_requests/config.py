from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestIdentityComponent,
)
try:
    import oarepo_workflows # noqa
    from oarepo_requests.actions.components import WorkflowTransitionComponent
    workflow_action_components = [WorkflowTransitionComponent]
except ImportError:
    workflow_action_components = []
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

REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    PublishDraftRequestType(),
]

REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

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
