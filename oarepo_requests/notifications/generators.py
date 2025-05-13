from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests.proxies import current_requests
from invenio_requests.records.api import Request

from oarepo_requests.proxies import current_notification_recipients_resolvers_registry

log = logging.getLogger("oarepo_requests.notifications.generators")

if TYPE_CHECKING:
    from typing import Any

    from invenio_notifications.models import Notification


class EntityRecipient(RecipientGenerator):
    """Recipient generator working as handler for generic entity."""

    def __init__(self, key: str):
        self.key = key

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """"""
        backend_ids = notification.context["backend_ids"]
        entity_ref_or_entity = dict_lookup(notification.context, self.key)

        if len(entity_ref_or_entity) != 1:
            # a hack - we need to have the original entity reference, not the resolved one
            entity_ref_or_entity = self._get_unresolved_entity_from_resolved(
                notification.context, self.key
            )
        if not entity_ref_or_entity:
            return

        entity_type = list(entity_ref_or_entity.keys())[0]

        for backend_id in backend_ids:
            generator = current_notification_recipients_resolvers_registry[entity_type][
                backend_id
            ](entity_ref_or_entity)
            generator(notification, recipients)

    def _get_unresolved_entity_from_resolved(self, context, key):
        """Get the unresolved entity from the resolved one."""
        match key.split(".", maxsplit=1):
            case "request", field:
                req = Request.get_record(context["request"]["id"])
                field_value = getattr(req, field)
                if field_value is not None:
                    return field_value.reference_dict
                return None
            case _:
                raise NotImplementedError(f"Can not resolve entity from key: {key}")


class SpecificEntityRecipient(RecipientGenerator):
    """Superclass for implementations of recipient generators for specific entities."""

    def __init__(self, key):
        self.key = key  # todo this is entity_reference, not path to entity as EntityRecipient, might be confusing

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients

    @abstractmethod
    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        raise NotImplementedError()

    def _resolve_entity(self) -> Any:
        entity_type = list(self.key)[0]
        registry = current_requests.entity_resolvers_registry

        registered_resolvers = registry._registered_types
        resolver = registered_resolvers.get(entity_type)
        proxy = resolver.get_entity_proxy(self.key)
        entity = proxy.resolve()
        return entity


class UserEmailRecipient(SpecificEntityRecipient):
    """User email recipient generator for a notification."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get user email of the entity."""
        # might be a system identity or a ghost user
        email = getattr(entity, "email", None)
        if email:
            return {email: Recipient(data={"email": email})}
        else:
            return {}


class GroupEmailRecipient(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data={"email": user.email})
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
                current_user_email = recipient_entity.email
                final_recipients[current_user_email] = Recipient(
                    data={"email": recipient_entity.email}
                )
            elif hasattr(recipient_entity, "emails"):
                for email in recipient_entity.emails:
                    final_recipients[email] = Recipient(data={"email": email})
            else:
                log.error(
                    "Entity %s %s does not have email/emails attribute, skipping.",
                    type(recipient_entity),
                    recipient_entity,
                )
                continue

        return final_recipients

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Get the emails from the multiple recipients entity."""
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients
