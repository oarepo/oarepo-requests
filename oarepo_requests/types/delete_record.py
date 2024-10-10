from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.delete_topic import DeleteTopicAcceptAction

from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class DeletePublishedRecordRequestType(NonDuplicableOARepoRequestType):
    type_id = "delete_published_record"
    name = _("Delete record")

    # Adding the extra_data attribute
    extra_data = {
        "dangerous": True,
        "hasForm": False,
        "editable": True,
    }

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": DeleteTopicAcceptAction,
        }

    description = _("Request deletion of published record")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)
