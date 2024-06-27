from invenio_users_resources.entity_resolvers import GroupResolver, UserResolver

from oarepo_requests.resolvers.ui import (
    FallbackEntityReferenceUIResolver,
    GroupEntityReferenceUIResolver,
    UserEntityReferenceUIResolver,
)
from oarepo_requests.types import (
    DeletePublishedRecordRequestType,
    EditPublishedRecordRequestType,
    PublishDraftRequestType
)

REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    PublishDraftRequestType(),
    # StatusChangingPublishDraftRequestType(),
]

REQUESTS_ALLOWED_RECEIVERS = ["user", "group"]

REQUESTS_ENTITY_RESOLVERS = [
    UserResolver(),
    GroupResolver(),
]

ENTITY_REFERENCE_UI_RESOLVERS = {
    "user": UserEntityReferenceUIResolver("user"),
    "fallback": FallbackEntityReferenceUIResolver("fallback"),
    "group": GroupEntityReferenceUIResolver("group"),
}

REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]
