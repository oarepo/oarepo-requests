# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Request for getting a membership of a group."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

import marshmallow as ma
from invenio_accounts.models import Role
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _
from invenio_requests.customizations.actions import CancelAction
from invenio_requests.resolvers.registry import ResolverRegistry

from oarepo_requests.actions.group_membership import (
    GroupMembershipAcceptAction,
    GroupMembershipDeclineAction,
    GroupMembershipSubmitAction,
)
from oarepo_requests.types import DefaultReceiverMixin, NonDuplicableOARepoRequestType

from ..utils import (
    classproperty,
    open_request_exists,
    request_identity_matches,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


class GroupMembershipRequestType(DefaultReceiverMixin[Role], NonDuplicableOARepoRequestType[Role]):
    """Request type for requesting membership in a group."""

    type_id = "group_membership"
    name = _("Request group membership")
    description = _("Request membership in a group")
    editable = False
    receiver_can_be_none = True

    allowed_topic_ref_types = ("group",)
    allowed_receiver_ref_types = ("group",)

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:  # noqa 805
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
        topic: Role,
        creator: dict[str, str] | Identity,
        data: dict,
    ) -> dict[str, str] | None:
        return {"group": "administration"}

    payload_schema: Mapping[str, ma.fields.Field] | None = {
        "justification": ma.fields.String(),
    }

    @override
    @classmethod
    def open_request_exists(
        cls, identity: Identity, topic: Role, creator: dict[str, str] | Any | None = None, **kwargs: Any
    ) -> bool:
        """Check whether the creator already has an open membership request for the group."""
        # same fallback as invenio's RequestsService.create when no explicit creator is passed
        if creator is None:
            creator = ResolverRegistry.reference_identity(identity)
        return open_request_exists(topic, cls.type_id, creator=creator)

    @override
    @staticmethod
    def topic_title(topic: Role | Mapping[str, Any] | None) -> str:
        """Return the group's title - its description, falling back to its name."""
        if not topic:
            return ""
        if isinstance(topic, Role):
            return str(topic.description or topic.name)
        return str(topic.get("description") or topic.get("name"))

    # UI and notifications pass the serialized group (a dict) instead of the resolved Role
    @override
    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Role | Mapping[str, Any] | None,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful name of the request."""
        group_title = self.topic_title(topic)
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
        topic: Role | Mapping[str, Any] | None,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
        group_title = self.topic_title(topic)

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
