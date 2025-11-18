#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Recipient generators for notifications."""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, cast, override

from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import EntityResolve, RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests.proxies import current_events_service, current_requests
from invenio_requests.records.api import Request
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service

from oarepo_requests.proxies import current_notification_recipients_resolvers_registry

log = logging.getLogger("oarepo_requests.notifications.generators")

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from invenio_notifications.models import Notification


def _extract_entity_email_data(entity: Any) -> dict[str, Any]:
    def _get(entity: Any, key: Any) -> Any:
        if isinstance(entity, dict) and key in entity:
            return entity.get(key, None)
        return getattr(entity, key, None)

    def _add(entity: Any, key: Any, res: dict, transform: Callable = lambda x: x) -> Any:
        v = _get(entity, key)
        if v:
            res[key] = transform(v)
            return v
        return None

    ret: dict[str, Any] = {}
    email = _add(entity, "email", ret)
    if not email:
        log.error(
            "Entity %s %s does not have email/emails attribute, skipping.",
            type(entity),
            entity,
        )
        return {}
    _add(entity, "preferences", ret, transform=lambda x: dict(x))
    _add(entity, "id", ret)

    return ret


class EntityRecipient(RecipientGenerator):
    """Recipient generator working as handler for generic entity."""

    def __init__(self, key: str):
        """Initialize the generator."""
        self.key = key

    def __call__(
        self, notification: Notification, recipients: dict[str, Recipient], backend_ids: list[str] | None = None
    ):
        """Generate recipients for the given entity."""
        backend_ids = backend_ids if backend_ids else notification.context["backend_ids"]
        entity_ref_or_entity = dict_lookup(notification.context, self.key)

        if len(entity_ref_or_entity) != 1:
            # a hack - we need to have the original entity reference, not the resolved one
            entity_ref_or_entity = self._get_unresolved_entity_from_resolved(notification.context, self.key)
        if not entity_ref_or_entity:
            return

        entity_type = next(iter(entity_ref_or_entity.keys()))

        for backend_id in backend_ids:
            generator_cls = current_notification_recipients_resolvers_registry.get(entity_type, {}).get(backend_id)
            if generator_cls:
                generator = generator_cls(entity_ref_or_entity)
                generator(notification, recipients)

    def _get_unresolved_entity_from_resolved(self, context: dict[str, Any], key: str) -> dict[str, str] | None:
        """Get the unresolved entity from the resolved one."""
        match key.split(".", maxsplit=1):
            case "request", field:
                req = Request.get_record(context["request"]["id"])
                field_value = getattr(req, field)
                if field_value is not None:
                    return cast("dict[str, str]", field_value.reference_dict)
                return None
            case _:
                raise NotImplementedError(f"Can not resolve entity from key: {key}")


class SpecificEntityRecipient(RecipientGenerator):
    """Superclass for implementations of recipient generators for specific entities."""

    def __init__(self, entity_reference: dict[str, str]):
        """Initialize the generator."""
        self._entity_reference = entity_reference

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):  # NOQA ARG002
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients

    @abstractmethod
    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        raise NotImplementedError

    def _resolve_entity(self) -> Any:
        entity_type = next(iter(self._entity_reference))
        registry = current_requests.entity_resolvers_registry

        # _registered_types missing in typing
        registered_resolvers = registry._registered_types  # noqa SLF001 # type: ignore[reportAttributeAccessIssue]
        resolver = registered_resolvers.get(entity_type)
        proxy = resolver.get_entity_proxy(self._entity_reference)
        return proxy.resolve()


class UserEmailRecipient(SpecificEntityRecipient):
    """User email recipient generator for a notification."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get user email of the entity."""
        # might be a system identity or a ghost user
        email = getattr(entity, "email", None)
        if email:
            return {email: Recipient(data=_extract_entity_email_data(entity))}
        return {}


class GroupEmailRecipient(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data=_extract_entity_email_data(user))
            for user in entity.users.all()
            if getattr(user, "email", None)
        }


class MultipleRecipientsEmailRecipients(SpecificEntityRecipient):
    """Recipient generator returning emails of entity with multiple recipients."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get recipient emails of entity with multiple recipients.."""
        final_recipients = {}
        for current_entity in entity.entities:
            recipient_entity = current_entity.resolve()
            if hasattr(recipient_entity, "email"):
                final_recipients[recipient_entity.email] = Recipient(data=_extract_entity_email_data(recipient_entity))
            elif hasattr(recipient_entity, "emails"):
                for email_data in recipient_entity.emails:
                    final_recipients[email_data["email"]] = Recipient(_extract_entity_email_data(email_data))
            else:
                log.error(
                    "Entity %s %s does not have email/emails attribute, skipping.",
                    type(recipient_entity),
                    recipient_entity,
                )
                continue
        return final_recipients


def __call__(self, notification: Notification, recipients: dict[str, Recipient]):  # noqa ARG002
    """Get the emails from the multiple recipients entity."""
    entity = self._resolve_entity()
    recipients.update(self._get_recipients(entity))
    return recipients


class RequestEntityResolve(EntityResolve):
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


class GeneralRequestParticipantsRecipient(RecipientGenerator):
    """Generalization of invenio RequestParticipantsRecipient capable of working with general entities.

    RequestParticipantsRecipient supports only users.
    """

    def __init__(self, key: str):
        """Ctor."""
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Fetch users involved in request and add as recipients."""
        request = dict_lookup(notification.context, self.key)

        # for invenio compatibility
        before_keys = set(recipients.keys())
        EntityRecipient("request.created_by")(notification, recipients, backend_ids=["email"])
        EntityRecipient("request.receiver")(notification, recipients, backend_ids=["email"])
        # can't replace the dict due to invenio pattern
        for id_ in set(recipients.keys()) - before_keys:
            recipients[str(recipients[id_].data["id"])] = recipients[id_]
            del recipients[id_]

        # assume events can only be done by users
        # fetching all request events to get involved users
        request_events = current_events_service.scan(
            identity=system_identity,
            extra_filter=dsl.Q("term", request_id=request["id"]),
        )
        # assume commenters can only be users
        user_ids = {re["created_by"]["user"] for re in request_events if re["created_by"].get("user")}

        filter_ = dsl.Q("terms", id=list(user_ids))
        users = current_users_service.scan(system_identity, extra_filter=filter_)
        for u in users:
            recipients[u["id"]] = Recipient(data=u)

        return recipients
