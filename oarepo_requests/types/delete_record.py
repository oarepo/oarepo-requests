from invenio_requests.customizations import RequestType

from oarepo_requests.actions.delete_topic import DeleteTopicAcceptAction

from .generic import OARepoRequestType


class DeleteRecordRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": DeleteTopicAcceptAction,
    }

    receiver_can_be_none = True
