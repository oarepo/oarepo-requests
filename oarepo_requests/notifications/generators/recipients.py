#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Notification recipients generators in oarepo-requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_access.permissions import system_identity
from invenio_notifications.models import Notification, Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests import current_events_service
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service

from oarepo_requests.notifications.generators.context import NotificationCtxWithReference
from oarepo_requests.proxies import current_notification_recipient_generators_registry

if TYPE_CHECKING:
    from invenio_accounts.models import User


def _extract_user_email_data(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "preferences": dict(user.preferences) if user.preferences else user.preferences,
        "email": user.email,
    }


class EntityRecipientGenerator(RecipientGenerator):
    """Recipient generator working as handler for generic entity."""

    def __init__(self, key: str):
        """Initialize the generator."""
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Generate recipients for the given entity."""
        if not isinstance(notification.context, NotificationCtxWithReference):
            raise TypeError(
                "Using EntityRecipientGenerator on notification without saved reference dictionary to the entity."
            )
        entity_type = notification.context.get_reference_type(self.key)
        generator = current_notification_recipient_generators_registry[entity_type](self.key, notification)
        generator(notification, recipients)


class MultipleRecipients(RecipientGenerator):
    """Recipient generator returning emails of entity with multiple recipients."""

    def __init__(self, key: str):
        """Initialize the generator."""
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Generate recipients for the given entity."""
        fields = dict_lookup(notification.context, self.key)

        for idx, entity_dict in enumerate(fields):
            type_ = next(iter(entity_dict.keys()))
            key = f"{self.key}.{idx}.{type_}"
            generator = current_notification_recipient_generators_registry[type_](key, notification)
            generator(notification, recipients)


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

        EntityRecipientGenerator("request.created_by")(notification, recipients)
        EntityRecipientGenerator("request.receiver")(notification, recipients)

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


# Do we need groups? Invenio doesn't seem to have GroupRecipient
"""
class GroupEmailRecipient(SpecificEntityRecipient):

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data=_extract_user_email_data(user))
            for user in entity.users.all()
            if getattr(user, "email", None)
        }
"""
