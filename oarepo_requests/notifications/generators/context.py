#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Notification context generators in oarepo-requests."""

from __future__ import annotations

import logging
from functools import wraps
from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_notifications.services import EntityResolverContextGenerator
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_requests import current_request_type_registry
from invenio_requests.records import Request

logger = logging.getLogger(__name__)  # TODO: correct celery logging?

if TYPE_CHECKING:
    from collections.abc import Callable

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


def save_reference[GeneratorT: EntityResolverContextGenerator](
    func: Callable[[GeneratorT, Notification], Notification],
) -> Callable[[GeneratorT, Notification], Notification]:
    """Save an entity reference after resolving it."""

    @wraps(func)
    def wrapped(self: GeneratorT, notification: Notification) -> Notification:
        entity_ref = dict_lookup(notification.context, self.key)
        if entity_ref is None:
            return notification
        notification = func(self, notification)
        notification.context = NotificationCtxWithReference(entity_ref, self.key, notification.context)
        return notification

    return wrapped


class ReferenceSavingEntityResolve(EntityResolverContextGenerator):
    """Entity resolver that saves the reference in the context."""

    @override
    @save_reference
    def __call__(self, notification: Notification) -> Notification:  # type: ignore[reportIncompatibleMethodOverride]
        """Resolve the entity and save its reference."""
        return super().__call__(notification)


class RequestTypeAwareEntityResolve(EntityResolverContextGenerator):
    """Entity resolver that saves the reference in the context."""

    @override
    @save_reference
    def __call__(self, notification: Notification) -> Notification:  # type: ignore[reportIncompatibleMethodOverride]
        """Resolve a draft and save its reference."""
        request = dict_lookup(notification.context, "request")
        if not request:
            logger.warning(
                "No request in notification context, the generator is probably used before the request is saved."
            )
        request_type = current_request_type_registry.lookup(request["type"], quiet=True)

        if not hasattr(request_type, "convert_topic_notifications"):
            return super().__call__(notification)

        entity_ref = dict_lookup(notification.context, self.key)
        entity_dict = request_type.convert_topic_notifications(entity_ref)
        dict_set(notification.context, self.key, entity_dict)
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
