from invenio_requests.customizations import RequestType
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .generic import OARepoRequestType


class PublishDraftRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": PublishDraftAcceptAction,
    }
    description = _("Request publishing of a draft")
    receiver_can_be_none = True
