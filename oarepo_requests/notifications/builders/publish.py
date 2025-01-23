from .oarepo import OARepoRequestActionNotificationBuilder

from ..generators import EntityRecipient


class PublishDraftRequestSubmitNotificationBuilder(OARepoRequestActionNotificationBuilder):
    type = "publish-draft-request-event.submit"

    recipients = [
        EntityRecipient(key="request.receiver")  # email only
    ]

class PublishDraftRequestAcceptNotificationBuilder(OARepoRequestActionNotificationBuilder):
    type = "publish-draft-request-event.accept"

    recipients = [
        EntityRecipient(key="request.created_by")
    ]