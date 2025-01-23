from invenio_notifications.backends import EmailNotificationBackend
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend

from invenio_users_resources.notifications.generators import (
    EmailRecipient,
)

class OARepoUserEmailBackend(UserEmailBackend):
    backend_id = EmailNotificationBackend.id

class OARepoRequestActionNotificationBuilder(NotificationBuilder):

    @classmethod
    def build(cls, request):
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "backend_ids": [backend.backend_id for backend in cls.recipient_backends]
            },
        )

    context = [
        EntityResolve(key="request"),
    ]

    recipient_backends = [OARepoUserEmailBackend()]





