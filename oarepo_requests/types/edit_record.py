import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.edit_topic import EditTopicAcceptAction

from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class EditPublishedRecordRequestType(NonDuplicableOARepoRequestType):
    type_id = "edit_published_record"
    name = _("Edit record")
    payload_schema = {
        "draft_record.links.self": ma.fields.Str(
            attribute="draft_record:links:self",
            data_key="draft_record:links:self",
        ),
        "draft_record.links.self_html": ma.fields.Str(
            attribute="draft_record:links:self_html",
            data_key="draft_record:links:self_html",
        ),
    }

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": EditTopicAcceptAction,
        }

    description = _("Request re-opening of published record")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)
