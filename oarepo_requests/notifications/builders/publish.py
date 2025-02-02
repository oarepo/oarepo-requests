from ..generators import EntityRecipient
from .oarepo import OARepoRequestActionNotificationBuilder


class PublishDraftRequestSubmitNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    type = "publish-draft-request-event.submit"

    recipients = [EntityRecipient(key="request.receiver")]  # email only


class PublishDraftRequestAcceptNotificationBuilder(
    OARepoRequestActionNotificationBuilder
):
    type = "publish-draft-request-event.accept"

    recipients = [EntityRecipient(key="request.created_by")]
