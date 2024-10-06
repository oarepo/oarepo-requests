from typing import Dict

import marshmallow as ma
from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import (
    PublishDraftAcceptAction,
    PublishDraftSubmitAction,
)

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
        "version": ma.fields.Str(),
    }
    extra_data = {
        "dangerous": False,
        "hasForm": True,
        "editable": True,
    }

    form = {
        "field": "version",
        "ui_widget": "Input",
        "props": {
            "label": _("Resource version"),
            "placeholder": _("Write down the version (first, second…)."),
            "required": False,
        },
    }

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "submit": PublishDraftSubmitAction,
            "accept": PublishDraftAcceptAction,
        }

    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if not topic.is_draft:
            raise ValueError("Trying to create publish request on published record")
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)
        topic_service = get_record_service_for_record(topic)
        topic_service.validate_draft(system_identity, topic["id"])

    @classmethod
    def can_possibly_create(self, identity, topic, *args, **kwargs):
        if not topic.is_draft:
            return False
        super_ = super().can_possibly_create(identity, topic, *args, **kwargs)
        return super_

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))
