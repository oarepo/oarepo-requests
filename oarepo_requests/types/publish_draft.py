from invenio_requests.customizations import RequestType

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .generic import OARepoRequestType


class PublishDraftRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": PublishDraftAcceptAction,
    }
    description = "request publishing of a draft"
    receiver_can_be_none = True
