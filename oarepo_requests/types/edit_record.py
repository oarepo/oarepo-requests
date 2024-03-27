from invenio_requests.customizations import RequestType
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.edit_topic import EditTopicAcceptAction
from oarepo_requests.actions.generic import AutoAcceptSubmitAction

from .generic import NonDuplicableOARepoRequestType


class EditRecordRequestType(NonDuplicableOARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "submit": AutoAcceptSubmitAction,
        "accept": EditTopicAcceptAction,
    }
    description = _("Request re-opening of published record")
    receiver_can_be_none = True
