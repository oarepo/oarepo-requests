#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from oarepo_requests.actions.publish_draft import (
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)

from ..actions.publish_draft import (
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)
from ..actions.publish_new_version import PublishNewVersionAcceptAction
from ..utils import classproperty, is_auto_approved, request_identity_matches
from .publish_base import PublishRequestType
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


class PublishNewVersionRequestType(PublishRequestType):
    """Request type for publication of a new version of a record."""

    type_id = "publish_new_version"
    name = _("Publish new version")
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

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": PublishDraftSubmitAction,
            "accept": PublishNewVersionAcceptAction,
            "decline": PublishDraftDeclineAction,
        }

    description = _("Request publishing of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    editable = False  # type: ignore

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if cls.topic_type(topic) != "new_version":
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
            return _("Publish new version")
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
                "Click to immediately publish the new version of the record. "
                "The draft will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            )

        if not request:
            return _(
                "By submitting the new version for review you are requesting the publication of the new version. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            )
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "The new version of the record has been submitted for review. "
                        "It is now locked and no further changes are possible. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "The new version of the record has been submitted for review. "
                        "You can now accept or decline the request."
                    )
                return _("The draft has been submitted for review.")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Submit for review. After submitting the new version for review, "
                        "it will be locked and no further modifications will be possible."
                    )
                return _("Request not yet submitted.")
