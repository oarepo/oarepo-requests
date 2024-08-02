from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestIdentityComponent,
    WorkflowTransitionComponent,
)
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
    # StatusChangingPublishDraftRequestType(),
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
        WorkflowTransitionComponent,
        RequestIdentityComponent,
    ],
    "submitted": [
        AutoAcceptComponent,
        WorkflowTransitionComponent,
        RequestIdentityComponent,
    ],
    "declined": [
        WorkflowTransitionComponent,
        RequestIdentityComponent,
    ],
    "cancelled": [
        WorkflowTransitionComponent,
        RequestIdentityComponent,
    ],
    "expired": [
        WorkflowTransitionComponent,
        RequestIdentityComponent,
    ],
}
