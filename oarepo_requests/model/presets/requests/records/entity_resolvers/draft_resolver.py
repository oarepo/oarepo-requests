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
from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.references import RecordResolver
from invenio_records_resources.references.entity_resolvers.records import (
    RecordProxy as InvenioRecordProxy,
)
from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultProxy as InvenioServiceResultProxy,
)
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


"""
from oarepo_runtime.records.entity_resolvers import (
    DraftProxy,
)

from oarepo_runtime.records.entity_resolvers import RecordResolver as BaseRecordResolver
"""


# TODO: temp
class RecordProxy(InvenioRecordProxy):
    """Resolver proxy for a record entity."""

    picked_fields = ("title", "creators", "contributors")

    def pick_resolved_fields(self, identity: Identity, resolved_dict: dict[str, Any]) -> dict[str, Any]:
        """Select which fields to return when resolving the reference."""
        resolved_fields = super().pick_resolved_fields(identity, resolved_dict)
        resolved_fields["links"] = resolved_dict.get("links", {})

        for fld in self.picked_fields:
            set_field(resolved_fields, resolved_dict, fld)

        return resolved_fields

    def ghost_record(self, value: dict[str, Any]) -> dict[str, Any]:
        """Return a ghost record."""
        return {
            **value,
            "metadata": {
                "title": "Deleted record",
            },
        }


class WithDeletedServiceResultProxy(InvenioServiceResultProxy):
    """Resolver proxy allowing deleted records."""

    @override
    def _resolve(self) -> dict[str, Any]:
        id_ = self._parse_ref_dict_id()
        # TODO: Make identity customizable
        return self.service.read(system_identity, id_, include_deleted=True).to_dict()


class DraftProxy(RecordProxy):
    """OARepo resolver proxy for drafts."""

    @override
    def _resolve(self) -> dict[str, Any]:
        pid_value = self._parse_ref_dict_id()
        try:
            return self.record_cls.pid.resolve(pid_value, registered_only=False)
        except (PIDUnregistered, NoResultFound):
            # try checking if it is a published record before failing
            return self.record_cls.pid.resolve(pid_value)


class DraftResolverPreset(Preset):
    """Preset for draft resolver."""

    provides = ("DraftResolver",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class DraftResolverMixin:
            """Mixin specifying draft resolver."""

            type_id = f"{builder.model.base_name}_draft"

            proxy_cls = DraftProxy

            def __init__(self, record_cls: type, service_id: str, type_key: str) -> None:
                super().__init__(record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls)

        yield AddClass(
            "DraftResolver",
            clazz=RecordResolver,
        )
        yield AddMixins(
            "DraftResolver",
            DraftResolverMixin,
        )
