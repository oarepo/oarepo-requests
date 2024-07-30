from invenio_users_resources.entity_resolvers import GroupResolver, UserResolver

from oarepo_requests.actions.components import (
    AutoAcceptComponent,
    RequestIdentityComponent,
    TopicStateChangeFromWorkflowComponent,
)
from oarepo_requests.resolvers.autoapprove import AutoApproveResolver
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

REQUESTS_ENTITY_RESOLVERS = [
    UserResolver(),
    GroupResolver(),
    AutoApproveResolver(),
]

ENTITY_REFERENCE_UI_RESOLVERS = {
    "user": UserEntityReferenceUIResolver("user"),
    "fallback": FallbackEntityReferenceUIResolver("fallback"),
    "group": GroupEntityReferenceUIResolver("group"),
}

REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]

REQUESTS_ACTION_COMPONENTS = [
    AutoAcceptComponent,
    TopicStateChangeFromWorkflowComponent,
    RequestIdentityComponent,
]  # komponenty; obj_or_import_string; can be callable
