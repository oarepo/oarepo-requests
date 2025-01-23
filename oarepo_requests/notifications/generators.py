from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from oarepo_requests.proxies import current_notification_recipients_resolvers_registry
from invenio_requests.proxies import current_requests

class EntityRecipient(RecipientGenerator):

    def __init__(self, key):
        """Ctor."""
        self.key = key

    def __call__(self, notification, recipients: dict):
        """Fetch community and add members as recipients, based on roles."""
        backend_ids = notification.context["backend_ids"]
        entity_ref = dict_lookup(notification.context, self.key)
        entity_type = list(entity_ref.keys())[0]
        for backend_id in backend_ids:
            generator = current_notification_recipients_resolvers_registry[entity_type][backend_id](entity_ref)
            generator(notification, recipients)

class SpecificEntityRecipient(RecipientGenerator):

    def __init__(self, key):
        self.key = key

    def _resolve_entity(self):
        entity_type = list(self.key)[0]
        registry = current_requests.entity_resolvers_registry

        registered_resolvers = registry._registered_types
        resolver = registered_resolvers.get(entity_type)
        proxy = resolver.get_entity_proxy(self.key)
        entity = proxy.resolve()
        return entity

class UserEmailRecipient(SpecificEntityRecipient):
    """User recipient generator for a notification."""

    def __call__(self, notification, recipients):
        """Update required recipient information and add backend id."""
        user = self._resolve_entity()
        email = user.email
        recipients[email] = Recipient(data={"email": email})