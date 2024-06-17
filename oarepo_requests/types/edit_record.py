from invenio_requests.customizations import RequestType
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.edit_topic import EditTopicAcceptAction
from oarepo_requests.actions.generic import AutoAcceptSubmitAction

from .ref_types import ModelRefTypes
from .generic import NonDuplicableOARepoRequestType


class EditPublishedRecordRequestType(NonDuplicableOARepoRequestType):
    type_id = "edit-published-record"
    name = _("Edit record")

    available_actions = {
        **RequestType.available_actions,
        "submit": AutoAcceptSubmitAction,
        "accept": EditTopicAcceptAction,
    }
    description = _("Request re-opening of published record")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)
