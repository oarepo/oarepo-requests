#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from ..utils import is_auto_approved, request_identity_matches
from .publish_base import PublishRequestType

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.records.api import Request


class PublishDraftRequestType(PublishRequestType):
    """Publish draft request type."""

    type_id = "publish_draft"
    name = _("Publish draft")

    payload_schema = {
        **PublishRequestType.payload_schema,
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
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if not topic.is_draft:
            return False

        index = topic.versions.index
        is_latest = topic.versions.is_latest

        if not (index == 1 and not is_latest):
            return False

        return super().is_applicable_to(identity, topic, *args, **kwargs)

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
            return _("Publish draft")
        if not request:
            return _("Submit for review")
        match request.status:
            case "submitted":
                return _("Submitted for review")
            case _:
                return _("Submit for review")

    @override
    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
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
