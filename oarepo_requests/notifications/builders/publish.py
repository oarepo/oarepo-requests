from ..generators import EntityRecipient
from .base import RequestActionNotificationBuilder


class PublishDraftRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    type = "publish-draft-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only


class PublishDraftRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    type = "publish-draft-request-event.accept"

    recipients = (EntityRecipient(key="request.created_by"),)


class PublishDraftRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    type = "publish-draft-request-event.decline"

    recipients = (EntityRecipient(key="request.created_by"),)
