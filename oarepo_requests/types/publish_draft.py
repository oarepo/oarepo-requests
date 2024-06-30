from invenio_requests.customizations import RequestType
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .ref_types import ModelRefTypes
from .generic import NonDuplicableOARepoRequestType
from ..actions.generic import OARepoSubmitAction, \
    OARepoDeclineAction


class PublishDraftRequestType(NonDuplicableOARepoRequestType):
    type_id = "publish-draft"
    name = _("Publish draft")

    available_actions = {
        **RequestType.available_actions,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
        "accept": PublishDraftAcceptAction,
    }
    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)