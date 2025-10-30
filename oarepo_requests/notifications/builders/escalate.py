from ..generators import EntityRecipient
from .base import RequestActionNotificationBuilder


class EscalateRequestSubmitNotificationBuilder(RequestActionNotificationBuilder):
    type = "escalate-request-event.submit"

    recipients = (EntityRecipient(key="request.receiver"),)  # email only
