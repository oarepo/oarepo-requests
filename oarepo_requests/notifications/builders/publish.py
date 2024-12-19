from .oarepo import OARepoNotificationBuilder
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend

from invenio_users_resources.notifications.generators import (
    EmailRecipient,
)

from ..generators import EntityRecipient, OARepoEntityResolve


class PublishDraftRequestSubmitNotificationBuilder(OARepoNotificationBuilder):
    type = "publish-draft-request-event.submit"

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
        OARepoEntityResolve(key="request"),
        OARepoEntityResolve(key="request.created_by"),
        OARepoEntityResolve(key="request.receiver")
    ]

    recipients = [
        EntityRecipient(key="request.receiver")  # email only
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]

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
        OARepoEntityResolve(key="request"),
        OARepoEntityResolve(key="request.created_by"),
        OARepoEntityResolve(key="request.receiver")
    ]

    recipients = [
        EntityRecipient(key="request.created_by")
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]