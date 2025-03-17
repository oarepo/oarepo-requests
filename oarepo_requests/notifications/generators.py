from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests.proxies import current_requests

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
        if len(entity_ref_or_entity) == 1:
            # it is entity reference
            entity_type = list(entity_ref_or_entity.keys())[0]
        else:
            # it is a resolved entity converted to a string - we have just a dictionary
            # The entity has been resolved for example when resolving created_by in
            # oarepo_requests/notifications/builders/oarepo.py - and we want to have
            # the resolver there as we want to use the identity of the user inside
            # the notification email.
            #
            # TODO: this is a nasty hack that should be done better
            if "email" in entity_ref_or_entity:
                # ok, looks like a user
                entity_ref_or_entity = {"user": entity_ref_or_entity["id"]}
                entity_type = "user"
            else:
                raise NotImplementedError(
                    f"Entity {entity_ref_or_entity} is not supported"
                )
        for backend_id in backend_ids:
            generator = current_notification_recipients_resolvers_registry[entity_type][
                backend_id
            ](entity_ref_or_entity)
            generator(notification, recipients)


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
        return {entity.email: Recipient(data={"email": entity.email})}


class GroupEmailRecipient(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data={"email": user.email})
            for user in entity.users.all()
        }


class MultipleRecipientsEmailRecipients(SpecificEntityRecipient):
    """Recipient generator returning emails of entity with multiple recipients."""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        """Get recipient emails of entity with multiple recipients.."""
        final_recipients = {}
        for current_entity in entity.entities:
            current_user = current_entity.resolve()
            if not hasattr(current_user, "email"):
                log.error(
                    "Entity %s %s does not have email attribute, skipping.",
                    type(current_user),
                    current_user,
                )
                continue
            current_user_email = current_user.email
            final_recipients[current_user_email] = Recipient(
                data={"email": current_user.email}
            )

        return final_recipients

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):
        """Get the emails from the multiple recipients entity."""
        entity = self._resolve_entity()
        recipients.update(self._get_recipients(entity))
        return recipients
