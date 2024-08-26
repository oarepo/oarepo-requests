import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction

from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class PublishDraftRequestType(NonDuplicableOARepoRequestType):
    type_id = "publish_draft"
    name = _("Publish draft")
    payload_schema = {
        "published_record.links.self": ma.fields.Str(
            attribute="published_record:links:self",
            data_key="published_record:links:self",
        ),
        "published_record.links.self_html": ma.fields.Str(
            attribute="published_record:links:self_html",
            data_key="published_record:links:self_html",
        ),
    }

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
