from invenio_requests.customizations import RequestType
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.delete_topic import DeleteTopicAcceptAction

from .generic import NonDuplicableOARepoRequestType


class DeletePublishedRecordRequestType(NonDuplicableOARepoRequestType):
    type_id = "delete-published-record"

    available_actions = {
        **RequestType.available_actions,
        "accept": DeleteTopicAcceptAction,
    }
    description = _("Request deletion of published record")
    receiver_can_be_none = True
