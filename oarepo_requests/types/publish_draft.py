from typing import Dict

import marshmallow as ma
from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from oarepo_requests.actions.publish_draft import (
    PublishDraftAcceptAction,
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)

from ..utils import is_auto_approved, request_identity_matches
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
            "decline": PublishDraftDeclineAction,
        }

    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    editable = False

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if not topic.is_draft:
            raise ValueError("Trying to create publish request on published record")
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)
        topic_service = get_record_service_for_record(topic)
        topic_service.validate_draft(system_identity, topic["id"])

    @classmethod
    def is_applicable_to(cls, identity, topic, *args, **kwargs):
        if not topic.is_draft:
            return False
        super_ = super().is_applicable_to(identity, topic, *args, **kwargs)
        return super_

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))

    @override
    def stateful_name(self, identity, *, topic, request=None, **kwargs):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _("Publish draft")
        if not request:
            return _("Submit for review")
        match request.status:
            case "submitted":
                return _("Submitted for review")
            case _:
                return _("Submit for review")

    @override
    def stateful_description(self, identity, *, topic, request=None, **kwargs):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _(
                "Click to immediately publish the draft. "
                "The draft will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            )

        if not request:
            return _(
                "By submitting the draft for review you are requesting the publication of the draft. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            )
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "The draft has been submitted for review. "
                        "It is now locked and no further changes are possible. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "The draft has been submitted for review. "
                        "You can now accept or decline the request."
                    )
                return _("The draft has been submitted for review.")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Submit for review. After submitting the draft for review, "
                        "it will be locked and no further modifications will be possible."
                    )
                return _("Request not yet submitted.")
