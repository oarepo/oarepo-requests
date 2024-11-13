from __future__ import annotations

import json
from typing import List, Set

from invenio_records_resources.references.entity_resolvers import EntityProxy
from invenio_records_resources.references.entity_resolvers.base import EntityResolver
from invenio_requests.resolvers.registry import ResolverRegistry
from flask_principal import Need



class MultipleRecipients:
    def __init__(self, recipients: List[dict]):
        self.recipients = recipients

    def resolve_entity(self) -> List[EntityProxy]:
        return [ResolverRegistry.resolve_entity(recipient) for recipient in self.recipients]

    def resolve_need(self) -> Set[Need]:
        needs = set()
        for recipient in self.recipients:
            recipient_needs = ResolverRegistry.resolve_need(recipient)
            needs.update(recipient_needs)
        return needs

    @classmethod
    def from_string_serialization(cls, string_serialization) -> MultipleRecipients:
        return cls(json.loads(string_serialization))

    def to_string_serialization(self) -> str:
        return json.dumps(self.recipients)

class MultipleRecipientsProxy(EntityProxy):
    def _resolve(self):
        value = self._parse_ref_dict_id()
        # value must be a string, we need to parse it to a list
        return MultipleRecipients.from_string_serialization(value)

    def get_needs(self, ctx=None):
        return self._resolve().resolve_need()

    def pick_resolved_fields(self, identity, resolved_dict):
        return {"multiple_recipients": resolved_dict["value"]}


class MultipleRecipientsResolver(EntityResolver):
    type_id = "multiple_recipients"

    def __init__(self):
        self.type_key = self.type_id
        super().__init__(
            None,
        )

    def matches_reference_dict(self, ref_dict):
        return self._parse_ref_dict_type(ref_dict) == self.type_id

    def _reference_entity(self, entity):
        return {self.type_key: str(entity.value)}

    def matches_entity(self, entity):
        return isinstance(entity, MultipleRecipients)

    def _get_entity_proxy(self, ref_dict):
        return MultipleRecipientsProxy(self, ref_dict)
