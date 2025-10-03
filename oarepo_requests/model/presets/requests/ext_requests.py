#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for processing request queries extension."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from invenio_rdm_records.records.api import RDMDraft, RDMRecord

from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)
from invenio_records_resources.services.records.results import RecordItem

# TODO: notification entity resolvers


class RDMPIDServiceResultResolver(ServiceResultResolver):
    """Service result resolver for draft records."""

    def _reference_entity(self, entity: RDMRecord | RDMDraft | RecordItem) -> dict[str, str]:
        pid = entity.id if isinstance(entity, RecordItem) else entity.pid
        return {self.type_key: str(pid)}
