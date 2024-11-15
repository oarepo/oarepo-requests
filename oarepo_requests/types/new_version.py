from typing import Dict

import marshmallow as ma
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request
from marshmallow.validate import OneOf
from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from ..actions.new_version import NewVersionAcceptAction
from ..utils import (
    get_record_service_for_record_cls,
    is_auto_approved,
    request_identity_matches,
)
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
        "keep_files": ma.fields.String(validate=OneOf(["true", "false"])),
    }

    def links(self, request, **kwargs):
        if request.status == "accepted":
            service = get_record_service_for_record_cls(request.topic.record_cls)
            record_item = service.read_draft(
                kwargs["identity"], request.topic._parse_ref_dict_id()
            )
            return {"topic_redirect_link": record_item["links"]["edit_html"]}

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": NewVersionAcceptAction,
        }

    description = _("Request requesting creation of new version of a published record.")
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)
    editable = False

    form = {
        "field": "keep_files",
        "ui_widget": "BooleanCheckbox",
        "props": {
            "label": _("Keep files"),
            "placeholder": _("Keep files in the new version?"),
            "required": False,
            "default": True,
        },
    }

    @classmethod
    def is_applicable_to(cls, identity, topic, *args, **kwargs):
        if topic.is_draft:
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if topic.is_draft:
            raise ValueError(
                "Trying to create new version request on draft record"
            )  # todo - if we want the active topic thing, we have to allow published as allowed topic and have to check this somewhere else
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))

    @override
    def stateful_name(self, identity, *, topic, request=None, **kwargs):
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return _("Request new version access")
        match request.status:
            case "submitted":
                return _("New version access requested")
            case _:
                return _("Request new version access")

    @override
    def stateful_description(self, identity, *, topic, request=None, **kwargs):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _("Click to start creating a new version of the record.")

        if not request:
            return _(
                "Request permission to update record (including files). "
                "You will be notified about the decision by email."
            )
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Permission to update record (including files) requested. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "You have been asked to approve the request to update the record. "
                        "You can approve or reject the request."
                    )
                return _("Permission to update record (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return _("Submit request to get edit access to the record.")
