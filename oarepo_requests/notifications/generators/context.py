#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Notification context generators in oarepo-requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_notifications.services.generators import EntityResolve
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_requests.records import Request

if TYPE_CHECKING:
    from invenio_notifications.models import Notification


class NotificationCtxWithReference(dict):
    """Context dict that keeps up separate dict with unresolved references."""

    def __init__(
        self, reference_dict: dict[str, str], reference_key: str, ctx: dict[str, Any] | NotificationCtxWithReference
    ):
        """Initialize the context."""
        super().__init__(ctx)
        self.references: dict[str, Any] = ctx.references if isinstance(ctx, NotificationCtxWithReference) else {}
        dict_set(self.references, reference_key, reference_dict)


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
        notification = super().__call__(notification)
        request_dict = notification.context["request"]
        if request_dict.get("title"):
            return request_dict

        request = Request.get_record(request_dict["id"])
        if hasattr(request.type, "stateful_name"):
            # If the request type has a stateful name, use it
            # note: do not have better identity here, so using system_identity
            # as a fallback
            request_dict["title"] = request.type.stateful_name(system_identity, topic=None)  # type: ignore[reportAttributeAccessIssue]
        return notification
