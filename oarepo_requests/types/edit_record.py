from invenio_requests.customizations import RequestType

from oarepo_requests.actions.edit_topic import EditTopicAcceptAction

from .generic import OARepoRequestType

from oarepo_runtime.i18n import lazy_gettext as _


class EditRecordRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": EditTopicAcceptAction,
    }
    description = _("Request re-opening of published record")
    receiver_can_be_none = True
