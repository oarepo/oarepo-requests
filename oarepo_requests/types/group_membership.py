#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request for getting a membership of a group."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import marshmallow as ma
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _
from invenio_requests.customizations.actions import CancelAction

from oarepo_requests.actions.group_membership import (
    GroupMembershipAcceptAction,
    GroupMembershipDeclineAction,
    GroupMembershipSubmitAction,
)
from oarepo_requests.types import DefaultReceiverMixin, OARepoRequestType

from ..utils import (
    classproperty,
    request_identity_matches,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


class GroupMembershipRequestType(DefaultReceiverMixin, OARepoRequestType):
    """Request type for requesting membership in a group."""

    type_id = "group_membership"
    name = _("Request group membership")  # type: ignore[reportAssignmentType]
    description = _("Request membership in a group")  # type: ignore[reportAssignmentType]
    editable = False
    receiver_can_be_none = True

    allowed_topic_ref_types = ["group"]  # noqa RUFF012
    allowed_receiver_ref_types = ["group"]  # noqa RUFF012 # type: ignore[reportAssignmentType]

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:  # noqa N805 # type: ignore[reportIncompatibleVariableOverride]
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "accept": GroupMembershipAcceptAction,
            "submit": GroupMembershipSubmitAction,
            "decline": GroupMembershipDeclineAction,
            # OARepoRequestType uses OARepoCancelAction using workflow; workflows are not supported for group topic
            "cancel": CancelAction,
        }

    @override
    @classmethod
    def default_request_receiver(
        cls,
        identity: Identity,
        topic: Record,
        creator: dict[str, str] | Identity,
        data: dict,
    ) -> dict[str, str] | None:
        return {"group": "administration"}

    payload_schema: Mapping[str, ma.fields.Field] | None = {
        "justification": ma.fields.String(),
    }

    @staticmethod
    def _group_title(topic: Record) -> str:
        """Return the group's title - its description, falling back to its name."""
        return str(topic.get("description") or topic.get("name"))

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
        group_title = self._group_title(topic)
        if not request:
            return gettext("Request membership in group '%(group)s'") % {"group": group_title}
        match request.status:
            case "submitted":
                return gettext("Membership in group '%(group)s' requested") % {"group": group_title}
            case _:
                return gettext("Request membership in group '%(group)s'") % {"group": group_title}

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
        group_title = self._group_title(topic)

        if not request:
            return gettext(
                "Request membership in group '%(group)s'. You will be notified about the decision by email."
            ) % {"group": group_title}
        match request.status:
            case "submitted":
                if request_identity_matches(request["created_by"], identity):
                    return gettext(
                        "Membership in group '%(group)s' requested. You will be notified about the decision by email."
                    ) % {"group": group_title}
                if request_identity_matches(request["receiver"], identity):
                    return gettext(
                        "You have been asked to approve the request for membership in group '%(group)s'. "
                        "You can approve or reject the request."
                    ) % {"group": group_title}
                return gettext("Membership in group '%(group)s' requested.") % {"group": group_title}
            case _:
                if request_identity_matches(request["created_by"], identity):
                    return gettext("Submit request to join group '%(group)s'.") % {"group": group_title}
                return gettext("This request for membership in group '%(group)s' has not yet been submitted.") % {
                    "group": group_title
                }
