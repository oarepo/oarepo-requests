#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for draft entity resolver creation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDUnregistered, PIDDoesNotExistError
from invenio_records_resources.references import RecordResolver
from invenio_rdm_records.requests.entity_resolvers import RDMRecordProxy

from oarepo_model.customizations import (
    AddClass,
    AddMixins,
    Customization,
)
from oarepo_model.presets import Preset
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from collections.abc import Generator

    from flask_principal import Identity
    from invenio_drafts_resources.records import Draft, Record
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


def set_field(result: dict[str, Any], resolved_dict: dict[str, Any], field_name: str) -> None:
    """Set field from resolved dict to result dict."""
    from_metadata = resolved_dict.get("metadata", {}).get(field_name)
    from_data = resolved_dict.get(field_name)

    if from_metadata:
        result.setdefault("metadata", {})[field_name] = from_metadata
    if from_data:
        result[field_name] = from_data


class OARepoRecordProxy(RDMRecordProxy):
    """Resolver proxy for a OARepo record entity.

    Based on RDMRecordProxy, supports customizable record and draft classes.
    """

    def __init__(self, resolver: RecordResolver, ref_dict: dict[str, str], record_cls: type[Record], draft_cls: type[Draft]):
        """Constructor.

        :param record_cls: The record class to use.
        """
        # this should be record resolver?
        super().__init__(resolver, ref_dict, record_cls) 
        self.draft_cls = draft_cls


    picked_fields = ("title", "creators", "contributors")

    def _get_record(self, pid_value):
        """Fetch the published record."""
        return self.record_cls.pid.resolve(pid_value)

    def _resolve(self):
        """Resolve the Record from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        draft = None
        try:
            draft = self.draft_cls.pid.resolve(pid_value, registered_only=False)
        except (PIDUnregistered, NoResultFound, PIDDoesNotExistError):
            # try checking if it is a published record before failing
            record = self._get_record(pid_value)
        else:
            # no exception raised. If published, get the published record instead
            record = draft if not draft.is_published else self._get_record(pid_value)

        return record

    def pick_resolved_fields(self, identity: Identity, resolved_dict: dict[str, Any]) -> dict[str, Any]:
        """Select which fields to return when resolving the reference."""
        resolved_fields: dict[str, Any] = super().pick_resolved_fields(identity, resolved_dict)
        resolved_fields["links"] = resolved_dict.get("links", {})

        for fld in self.picked_fields:
            set_field(resolved_fields, resolved_dict, fld)

        return resolved_fields
    
    # TODO: test
    def ghost_record(self, value: dict[str, Any]) -> dict[str, Any]:
        # TODO: important!!! security implications on sensitive metadata
        service = self._resolver.get_service()
        if hasattr(service, "read_draft"):
            try:
                draft_dict = service.read_draft(system_identity, value["id"]).to_dict()
                return self.pick_resolved_fields(system_identity, draft_dict)
            except PIDDoesNotExistError:
                return {
                    **value,
                    "metadata": {
                        "title": "Deleted record",
                    },
                }
            
class OARepoRecordResolver(RecordResolver):
    """Record resolver for OARepo records.

    Based on RDMRecordResolver, supports customizable record and draft classes.
    """
    # TODO: subclassed records_resources instead of RDM because of __init__ hardcoded record_cls and draft_cls, discuss maintainability
    proxy_cls = OARepoRecordProxy

    def __init__(self, record_cls: type[Record], draft_cls: type[Draft], service_id: str, type_key: str) -> None:
        super().__init__(record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls)
        self.draft_cls = draft_cls

    def _get_entity_proxy(self, ref_dict):
        """Return a RecordProxy for the given reference dict."""
        return self.proxy_cls(self, ref_dict, self.record_cls, self.draft_cls)

    def matches_entity(self, entity):
        """Check if the entity is a draft or a record."""
        return isinstance(entity, (self.draft_cls, self.record_cls))
            

class RequestsResolverPreset(Preset):
    """Preset for draft resolver."""

    provides = ("RecordResolver",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class ResolverMixin:
            """Mixin specifying record resolver."""

            type_id = f"{builder.model.base_name}"


        yield AddClass(
            "RecordResolver",
            clazz=OARepoRecordResolver,
        )
        yield AddMixins(
            "RecordResolver",
            ResolverMixin,
        )
