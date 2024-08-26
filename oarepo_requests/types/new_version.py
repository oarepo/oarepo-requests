import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _

from ..actions.new_version import NewVersionAcceptAction
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class NewVersionRequestType(
    NonDuplicableOARepoRequestType
):  # NewVersionFromPublishedRecord? or just new_version
    type_id = "new_version"
    name = _("New Version")
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
            "accept": NewVersionAcceptAction,
        }

    description = _("Request requesting creation of new version of a published record.")
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)
