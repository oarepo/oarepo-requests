#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator
from oarepo_model.customizations import (
    AddClass,
    AddMixins,
    Customization,
)
from oarepo_model.model import Dependency, InvenioModel
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder

from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.references.entity_resolvers.records import (
    RecordProxy as InvenioRecordProxy,
)
from sqlalchemy.exc import NoResultFound
from invenio_access.permissions import system_identity
from invenio_records_resources.references.entity_resolvers.results import ServiceResultProxy as InvenioServiceResultProxy


def set_field(result, resolved_dict, field_name):
    from_metadata = resolved_dict.get("metadata", {}).get(field_name)
    from_data = resolved_dict.get(field_name)

    if from_metadata:
        result.setdefault("metadata", {})[field_name] = from_metadata
    if from_data:
        result[field_name] = from_data
from invenio_records_resources.references import RecordResolver
"""
from oarepo_runtime.records.entity_resolvers import (
    DraftProxy,
)

from oarepo_runtime.records.entity_resolvers import RecordResolver as BaseRecordResolver
"""
#TODO: temp
class RecordProxy(InvenioRecordProxy):
    picked_fields = ["title", "creators", "contributors"]

    def pick_resolved_fields(self, identity, resolved_dict):
        """Select which fields to return when resolving the reference."""
        resolved_fields = super().pick_resolved_fields(identity, resolved_dict)

        for fld in self.picked_fields:
            set_field(resolved_fields, resolved_dict, fld)

        return resolved_fields

    def ghost_record(self, value):
        return {
            **value,
            "metadata": {
                "title": "Deleted record",
            },
        }

class WithDeletedServiceResultProxy(InvenioServiceResultProxy):
    """Resolver proxy for a result item entity."""

    def _resolve(self):
        """Resolve the result item from the proxy's reference dict."""
        id_ = self._parse_ref_dict_id()
        # TODO: Make identity customizable
        return self.service.read(system_identity, id_, include_deleted=True).to_dict()


class DraftProxy(RecordProxy):
    def _resolve(self):
        pid_value = self._parse_ref_dict_id()
        try:
            return self.record_cls.pid.resolve(pid_value, registered_only=False)
        except (PIDUnregistered, NoResultFound):
            # try checking if it is a published record before failing
            return self.record_cls.pid.resolve(pid_value)


class DraftResolverPreset(Preset):

    provides = (
        "DraftResolver",
    )

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization, None, None]:

        class DraftResolverMixin:
            """Base class for records in the model.
            This class extends InvenioRecord and can be customized further.
            """

            type_id = f"{builder.model.base_name}_draft"

            proxy_cls = DraftProxy

            def __init__(self, record_cls, service_id, type_key):
                super().__init__(
                    record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls
                )

        yield AddClass(
            "DraftResolver",
            clazz=RecordResolver,
        )
        yield AddMixins(
            "DraftResolver",
            DraftResolverMixin,
        )