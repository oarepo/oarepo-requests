from typing import Dict

import marshmallow as ma
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
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
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    @classmethod
    def can_possibly_create(self, identity, topic, *args, **kwargs):
        if topic.is_draft:
            return False
        return super().can_possibly_create(identity, topic, *args, **kwargs)

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if topic.is_draft:
            raise ValueError(
                "Trying to create new version request on draft record"
            )  # todo - if we want the active topic thing, we have to allow published as allowed topic and have to check this somewhere else
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))
