from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests.proxies import current_requests

from oarepo_requests.proxies import current_notification_recipients_resolvers_registry

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
        entity_ref = dict_lookup(notification.context, self.key)
        entity_type = list(entity_ref.keys())[0]
        for backend_id in backend_ids:
            generator = current_notification_recipients_resolvers_registry[entity_type][
                backend_id
            ](entity_ref)
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
    """Recipient generator returning emails of the members of the recipient group"""

    def _get_recipients(self, entity: Any) -> dict[str, Recipient]:
        return {
            user.email: Recipient(data={"email": user.email})
            for user in entity.users.all()
        }

class MultipleRecipientsEmailRecipients(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group"""

    def __call__(self, notification: Notification, recipients: dict[str, Recipient]):

        entity = self._resolve_entity()
        print(f'blahblahblah3, {type(entity)=}')

        print(f'{type(entity)=}')
        print(f'blahblahblah2')
        print(f'{entity.entities=}')
        for current_entity in entity.entities:
            print(f'{type(current_entity)=}')


        raise ValueError()
        return {
            user.email: Recipient(data={"email": user.email})
            for user in entity.users.all()
        }
