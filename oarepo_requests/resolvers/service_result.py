#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Service result resolvers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)

if TYPE_CHECKING:
    from typing import Any

    from invenio_rdm_records.records.api import RDMDraft
    from invenio_records_resources.services.records.results import RecordItem


class DraftServiceResultResolver(ServiceResultResolver):
    """Service result resolver for draft records, needed for RDM drafts."""

    # TODO: specific type for entity reference?
    def _reference_entity(self, entity: RDMDraft | RecordItem) -> dict[str, str]:
        """Create a reference dict for the given result item."""
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}

    @property
    def draft_cls(self) -> type:  # TODO: type[RDMDraft] -> works with subclasses?
        """Get specified draft class or from service."""
        return self.get_service().draft_cls

    def matches_entity(self, entity: Any) -> bool:
        """Check if the entity is a draft."""
        if isinstance(entity, self.draft_cls):
            return True

        return super().matches_entity(entity=entity)
