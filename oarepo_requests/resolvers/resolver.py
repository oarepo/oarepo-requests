#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Record entity resolver with draft support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.records import RDMDraft
from invenio_rdm_records.requests.entity_resolvers import RDMRecordProxy, RDMRecordResolver
from invenio_rdm_records.services import RDMRecordServiceConfig

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_rdm_records.services.services import RDMRecordService


class RecordProxy(RDMRecordProxy):
    """Record proxy that supports resolving drafts."""

    def ghost_record(self, record: dict[str, str]) -> dict[str, Any]:
        """Ghost representation of a record.

        Drafts at the moment cannot be resolved, service.read_many() is searching on
        public records, thus the `ghost_record` method will always kick in!
        Supports checking whether the record is draft without published record that the find_many method fails to find.
        """
        # TODO: important!!! read_draft with system_identity has security implications on sensitive metadata

        service = cast("RDMRecordService", self._resolver.get_service())
        try:
            draft_dict = service.read_draft(system_identity, record["id"]).to_dict()
            return self.pick_resolved_fields(system_identity, draft_dict)  # type: ignore[no-any-return]
        except PIDDoesNotExistError:
            return super().ghost_record(record)  # type: ignore[no-any-return]

    @override
    def pick_resolved_fields(self, identity: Identity, resolved_dict: dict[str, Any]) -> dict[str, Any]:
        """Select which fields to return when resolving the reference."""
        resolved_fields: dict[str, Any] = super().pick_resolved_fields(identity, resolved_dict)
        resolved_fields["links"] = resolved_dict.get("links", {})
        return resolved_fields


class RecordResolver(RDMRecordResolver):
    """RDM Record entity resolver."""

    type_id = "record"

    def __init__(self):
        """Initialize the resolver."""
        super(RDMRecordResolver, self).__init__(
            RDMDraft,
            RDMRecordServiceConfig.service_id,  # type: ignore[reportArgumentType]
            type_key=self.type_id,
            proxy_cls=RecordProxy,
        )
