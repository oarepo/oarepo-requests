from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator, EntityResolve
from invenio_records.dictutils import dict_lookup
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service

from invenio_communities.proxies import current_communities
from abc import ABC, abstractmethod

from invenio_records.dictutils import dict_lookup, dict_set

from invenio_notifications.backends.email import EmailNotificationBackend
from invenio_notifications.registry import EntityResolverRegistry


class OARepoEntityResolve(EntityResolve):
    """Payload generator for a notification using the entity resolvers."""

    def __init__(self, key):
        """Ctor."""
        self.key = key

    def __call__(self, notification):
        """Update required recipient information and add backend id."""
        entity_ref = dict_lookup(notification.context, self.key)
        entity = EntityResolverRegistry.resolve_entity(entity_ref)
        entity["_entity_ref"] = entity_ref
        dict_set(notification.context, self.key, entity)
        return notification

class EntityRecipient(RecipientGenerator):


    def __init__(self, key):
        """Ctor."""
        self.key = key

    def __call__(self, notification, recipients: dict):
        """Fetch community and add members as recipients, based on roles."""
        from invenio_requests.resolvers.registry import ResolverRegistry
        from invenio_requests.proxies import current_requests

        registry = current_requests.entity_resolvers_registry
        entity = dict_lookup(notification.context, self.key)
        ref_dict = entity["_entity_ref"]
        type_ = list(ref_dict.keys())[0]
        registered_resolvers = registry._registered_types
        resolver = registered_resolvers.get(type_)
        proxy = resolver.get_entity_proxy(ref_dict)
        email_recipients = proxy.get_recipients(ctx={"notification": notification}, resolved_entity=entity)
        for email in email_recipients:
            recipients[email] = Recipient(data={"email": email})
        return recipients