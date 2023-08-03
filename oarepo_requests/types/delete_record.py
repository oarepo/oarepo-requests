from invenio_requests.customizations import RequestType

from oarepo_requests.actions.delete_topic import DeleteTopicSubmitAction


class DeleteRecordRequestType(RequestType):

    available_actions = {
        **RequestType.available_actions,
        "submit": DeleteTopicSubmitAction,
    }

    receiver_can_be_none = True