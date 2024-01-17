from invenio_requests.customizations import RequestType

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .generic import OARepoRequestType


class PublishDraftRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": PublishDraftAcceptAction,
    }

    receiver_can_be_none = True
