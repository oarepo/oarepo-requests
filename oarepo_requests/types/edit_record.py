from typing import Dict

import marshmallow as ma
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from oarepo_requests.actions.edit_topic import EditTopicAcceptAction

from ..utils import is_auto_approved, request_identity_matches
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
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    @classmethod
    def is_applicable_to(cls, identity, topic, *args, **kwargs):
        if topic.is_draft:
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if topic.is_draft:
            raise ValueError(
                "Trying to create edit request on draft record"
            )  # todo - if we want the active topic thing, we have to allow published as allowed topic and have to check this somewhere else
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))

    @override
    def stateful_name(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return _("Request edit access")
        match request.status:
            case "submitted":
                return _("Edit access requested")
            case _:
                return _("Request edit access")

    @override
    def stateful_description(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _("Click to start editing the metadata of the record.")

        if not request:
            return _(
                "Request edit access to the record. "
                "You will be notified about the decision by email."
            )
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Edit access requested. You will be notified about "
                        "the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "You have been requested to grant edit access to the record."
                    )
                return _("Edit access requested.")
            case _:
                return _(
                    "Request edit access to the record. "
                    "You will be notified about the decision by email."
                )
