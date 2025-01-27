from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_requests.proxies import current_requests

from oarepo_requests.proxies import current_notification_recipients_resolvers_registry

if TYPE_CHECKING:
    from invenio_notifications.models import Notification


class EntityRecipient(RecipientGenerator):
    """Recipient generator working as handler for generic entity."""

    def __init__(self, key: str):

        self.key = key

    def __call__(self, notification: Notification, recipients: dict):
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

    def __init__(self, key):
        self.key = key  # todo this is entity_reference, not path to entity as EntityRecipient, might be confusing

    def _resolve_entity(self):
        entity_type = list(self.key)[0]
        registry = current_requests.entity_resolvers_registry

        registered_resolvers = registry._registered_types
        resolver = registered_resolvers.get(entity_type)
        proxy = resolver.get_entity_proxy(self.key)
        entity = proxy.resolve()
        return entity


class UserEmailRecipient(SpecificEntityRecipient):
    """User email recipient generator for a notification."""

    def __call__(self, notification: Notification, recipients: dict):
        """Update required recipient information."""
        user = self._resolve_entity()
        email = user.email
        recipients[email] = Recipient(data={"email": email})


class GroupEmailRecipient(SpecificEntityRecipient):
    """Recipient generator returning emails of the members of the recipient group"""

    def __call__(self, notification: Notification, recipients: dict):
        """Update required recipient information."""
        group = self._resolve_entity()
        users_query = group.users
        users = users_query.all()
        mails = [u.email for u in users]
        for mail in mails:
            recipients[mail] = Recipient(data={"email": mail})
