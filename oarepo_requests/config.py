from oarepo_requests.resolvers.ui import UserEntityReferenceUIResolver, FallbackEntityReferenceUIResolver, \
    GroupEntityReferenceUIResolver
from oarepo_requests.types import DeletePublishedRecordRequestType, EditPublishedRecordRequestType, PublishDraftRequestType
from invenio_users_resources.entity_resolvers import UserResolver, GroupResolver


REQUESTS_REGISTERED_TYPES = [
    DeletePublishedRecordRequestType(),
    EditPublishedRecordRequestType(),
    PublishDraftRequestType(),
]

REQUESTS_ALLOWED_RECEIVERS = [
    "user", "role"
]

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