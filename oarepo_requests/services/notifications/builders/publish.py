from .oarepo import OARepoNotificationBuilder
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend

from invenio_users_resources.notifications.generators import (
    EmailRecipient,
)

class PublishDraftRequestAcceptNotificationBuilder(OARepoNotificationBuilder):
    type = "publish-draft-request-event.accept"

    @classmethod
    def build(cls, request):
        """Build notification with context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request)
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.receiver")
    ]

    recipients = [
        EmailRecipient(key="request.created_by.email"),  # email only
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]