from invenio_access.permissions import system_process
from invenio_records_resources.references.entity_resolvers import EntityProxy


class AutoApprover:
    def __init__(self, value):
        self.value = value


class AutoApproveProxy(EntityProxy):

    def _resolve(self):
        value = self._parse_ref_dict_id()
        return AutoApprover(value)

    def get_needs(self, ctx=None):
        return [system_process]

    def pick_resolved_fields(self, identity, resolved_dict):
        return {"value": resolved_dict["value"]}


from invenio_records_resources.references.entity_resolvers.base import EntityResolver


class AutoApproveResolver(EntityResolver):
    type_id = "auto_approve"

    def __init__(self):
        self.type_key = self.type_id
        super().__init__(
            None,
        )

    def matches_reference_dict(self, ref_dict):
        return self._parse_ref_dict_type(ref_dict) == self.type_id

    def _reference_entity(self, entity):
        return {"auto_approve": str(entity.value)}

    def matches_entity(self, entity):
        return isinstance(entity, AutoApprover)

    def _get_entity_proxy(self, ref_dict):
        return AutoApproveProxy(self, ref_dict)
