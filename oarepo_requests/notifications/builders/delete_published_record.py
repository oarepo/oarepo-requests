from invenio_notifications.services.generators import EntityResolve

from ..generators import EntityRecipient
from .base import RequestActionNotificationBuilder


class DeletePublishedRecordRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    type = "delete-published-record-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only


class DeletePublishedRecordRequestAcceptNotificationBuilder(RequestActionNotificationBuilder):
    type = "delete-published-record-request-event.accept"

    recipients = (EntityRecipient(key="request.created_by"),)

    context = (EntityResolve(key="request"),)


class DeletePublishedRecordRequestDeclineNotificationBuilder(RequestActionNotificationBuilder):
    type = "delete-published-record-request-event.decline"

    recipients = (EntityRecipient(key="request.created_by"),)
