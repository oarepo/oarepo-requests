#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING

import marshmallow as ma
from oarepo_runtime.i18n import lazy_gettext as _

from ..actions.publish_draft import (
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)
from ..actions.publish_new_version import PublishNewVersionAcceptAction
from ..utils import classproperty
from .ref_types import ModelRefTypes

if TYPE_CHECKING:
    from invenio_requests.customizations.actions import RequestAction


from .publish_draft import PublishDraftRequestType


class PublishNewVersionRequestType(PublishDraftRequestType):
    """Publish draft request type."""

    type_id = "publish_new_version"
    name = _("Publish new version")
    payload_schema = {
        **PublishDraftRequestType.payload_schema,
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
