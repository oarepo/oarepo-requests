from invenio_users_resources.entity_resolvers import UserResolver, UserProxy
from invenio_notifications.models import Recipient

class OARepoUserProxy(UserProxy):
    def get_recipients(self, ctx: dict, resolved_entity: dict, **kwargs):
        return [resolved_entity['email']]

class OARepoUserResolver(UserResolver):
    def _get_entity_proxy(self, ref_dict):
        """Return a UserProxy for the given reference dict."""
        return OARepoUserProxy(self, ref_dict)