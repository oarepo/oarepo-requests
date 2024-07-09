from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class PublishDraftRequestType(NonDuplicableOARepoRequestType):
    type_id = "publish-draft"
    name = _("Publish draft")

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": PublishDraftAcceptAction,
        }

    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)
