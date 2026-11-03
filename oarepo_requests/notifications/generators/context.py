# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Notification context generators in oarepo-requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_notifications.services.generators import EntityResolve
from invenio_records.dictutils import dict_lookup
from invenio_requests.records import Request

if TYPE_CHECKING:
    from invenio_notifications.models import Notification


class NotificationCtxWithReference(dict):
    """Context dict that keeps up separate dict with unresolved references."""

    def __init__(
        self,
        reference_dict: dict[str, str],
        reference_key: str,
        ctx: dict[str, Any] | NotificationCtxWithReference,
    ):
        """Initialize the context."""
        super().__init__(ctx)
        self.references: dict[str, dict[str, str]] = (
            ctx.references if isinstance(ctx, NotificationCtxWithReference) else {}
        )
        self.references[reference_key] = reference_dict

    def get_reference_type(self, key: str) -> str:
        """Get the type of the reference stored under the given key."""
        return next(iter(self.references[key].keys()))


class ReferenceSavingEntityResolve(EntityResolve):
    """Entity resolver that saves the reference in the context."""

    @override
    def __call__(self, notification: Notification):
        entity_ref = dict_lookup(notification.context, self.key)
        if entity_ref is None:
            return notification
        notification = super().__call__(notification)
        notification.context = NotificationCtxWithReference(entity_ref, self.key, notification.context)
        return notification


class RequestEntityResolve(ReferenceSavingEntityResolve):
    """Entity resolver that adds the correct title if it is missing."""

    @override
    def __call__(self, notification: Notification):
        # request types import notification builders, which import this module
        from oarepo_requests.types import RequestTypeWithStatefulName

        notification = super().__call__(notification)
        request_dict = notification.context["request"]
        if request_dict.get("title"):
            return request_dict

        request = Request.get_record(request_dict["id"])
        if isinstance(request.type, RequestTypeWithStatefulName):
            # If the request type has a stateful name, use it
            # note: do not have better identity here, so using system_identity
            # as a fallback
            request_dict["title"] = request.type.stateful_name(system_identity, request=request, topic=None)
        return notification
