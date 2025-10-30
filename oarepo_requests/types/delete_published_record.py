#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request for deleting published record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, override

import marshmallow as ma
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _

from oarepo_requests.actions.delete_published_record import (
    DeletePublishedRecordAcceptAction,
    DeletePublishedRecordDeclineAction,
)

from ..utils import (
    classproperty,
    is_auto_approved,
    open_request_exists,
    request_identity_matches,
)
from .generic import NonDuplicableOARepoRecordRequestType

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request

    from ..utils import JsonValue


class DeletePublishedRecordRequestType(NonDuplicableOARepoRecordRequestType):
    """Request type for requesting deletion of a published record."""

    type_id = "delete_published_record"
    name = _("Delete record")  # type: ignore[reportAssignmentType]
    description = _("Request deletion of published record")  # type: ignore[reportAssignmentType]
    allowed_on_draft = False
    editable = False
    dangerous = True
    receiver_can_be_none = True

    payload_schema: Mapping[str, ma.fields.Field] | None = {
        "removal_reason": ma.fields.Str(required=True),
        "note": ma.fields.Str(),
    }

    @classmethod
    def is_applicable_to(cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any) -> bool:
        """Check if the request type is applicable to the topic."""
        if open_request_exists(topic, cls.type_id):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:  # noqa N805
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "accept": DeletePublishedRecordAcceptAction,
            "decline": DeletePublishedRecordDeclineAction,
        }

    # TODO: used in ui
    form: ClassVar[JsonValue] = [
        {
            "section": "",
            "fields": [
                {
                    "field": "removal_reason",
                    "ui_widget": "Input",
                    "props": {
                        "label": _("Removal Reason"),
                        "placeholder": _("Write down the removal reason."),
                        "required": True,
                    },
                },
                {
                    "section": "",
                    "field": "note",
                    "ui_widget": "Input",
                    "props": {
                        "label": _("Note"),
                        "placeholder": _("Write down the additional note."),
                        "required": False,
                    },
                },
            ],
        }
    ]

    @override
    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful name of the request."""
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return gettext("Request record deletion")
        match request.status:
            case "submitted":
                return gettext("Record deletion requested")
            case _:
                return gettext("Request record deletion")

    @override
    def stateful_description(  # noqa PLR0911
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
        if is_auto_approved(self, identity=identity, topic=topic):
            return gettext("Click to permanently delete the record.")

        if not request:
            return gettext("Request permission to delete the record.")
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return gettext(
                        "Permission to delete record requested. You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return gettext(
                        "You have been asked to approve the request to permanently delete the record. "
                        "You can approve or reject the request."
                    )
                return gettext("Permission to delete record (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return gettext("Submit request to get permission to delete the record.")
                return gettext("You do not have permission to delete the record.")
