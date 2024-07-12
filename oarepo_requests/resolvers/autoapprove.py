from invenio_access.permissions import system_process
from invenio_records_resources.references.entity_resolvers import EntityProxy


class AutoApprover:
    def __init__(self, value):
        self.value = value


class AutoApproveProxy(EntityProxy):
    """Resolver proxy for a User entity."""

    def _resolve(self):
        value = self._parse_ref_dict_id()
        return AutoApprover(value)

    def get_needs(self, ctx=None):
        return [system_process]

    def pick_resolved_fields(self, identity, resolved_dict):
        """Select which fields to return when resolving the reference."""
        return {"value": resolved_dict["value"]}


from invenio_records_resources.references.entity_resolvers.base import EntityResolver


class AutoApproveResolver(EntityResolver):
    """Community entity resolver.

    The entity resolver enables Invenio-Requests to understand communities as
    receiver and topic of a request.
    """

    type_id = "auto_approve"
    """Type identifier for this resolver."""

    def __init__(self):
        """Initialize the default record resolver."""
        self.type_key = self.type_id
        super().__init__(
            None,
        )

    def matches_reference_dict(self, ref_dict):
        """Check if the reference dict references a user."""
        return self._parse_ref_dict_type(ref_dict) == self.type_id

    def _reference_entity(self, entity):
        """Create a reference dict for the given user."""
        return {"auto_approve": str(entity.value)}

    def matches_entity(self, entity):
        """Check if the entity is a user."""
        return isinstance(entity, AutoApprover)

    def _get_entity_proxy(self, ref_dict):
        """Return a UserProxy for the given reference dict."""
        return AutoApproveProxy(self, ref_dict)
