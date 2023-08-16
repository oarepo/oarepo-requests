from invenio_requests.customizations import RequestType

from oarepo_requests.actions.publish_draft import PublishDraftSubmitAction


class PublishDraftRequestType(RequestType):

    available_actions = {
        **RequestType.available_actions,
        "submit": PublishDraftSubmitAction,
    }

    receiver_can_be_none = True
