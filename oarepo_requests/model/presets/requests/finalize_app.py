#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for defining finalize_app entrypoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from invenio_rdm_records.requests.entity_resolvers import RDMRecordServiceResultProxy
from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)
from oarepo_model.customizations import (
    AddEntryPoint,
    AddModule,
    AddToModule,
    Customization,
)
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from collections.abc import Generator

    from flask import Flask
    from invenio_rdm_records.records.api import RDMDraft, RDMRecord
    from invenio_records_resources.references import RecordResolver
    from invenio_records_resources.services.records.results import RecordItem
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


# TODO: R01
class DraftServiceResultResolver(ServiceResultResolver):
    """Service result resolver for draft records."""

    def _reference_entity(self, entity: RDMRecord | RDMDraft | RecordItem) -> dict[str, str]:
        """Create a reference dict for the given result item."""
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}

    @property
    def draft_cls(self):
        """Get specified draft class or from service."""
        return self.get_service().draft_cls

    def matches_entity(self, entity):
        """Check if the entity is a draft."""
        if isinstance(entity, self.draft_cls):
            return True

        return super().matches_entity(entity=entity)


class RequestsFinalizeAppPreset(Preset):
    """Preset for extension class."""

    depends_on = ("RecordResolver", "Record", "Draft")

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        def finalize_app(app: Flask) -> None:
            service_id = builder.model.base_name
            model_entity_resolver = cast("type[RecordResolver]", dependencies.get("RecordResolver"))(
                record_cls=dependencies.get("Record"),
                # TODO: R01
                draft_cls=dependencies.get("Draft"),  # type: ignore[reportCallIssue]
                service_id=service_id,
                type_key=service_id,
            )
            app.extensions["invenio-requests"].entity_resolvers_registry.register_type(model_entity_resolver)

            notification_resolver = DraftServiceResultResolver(
                service_id=service_id,
                type_key=service_id,
                proxy_cls=RDMRecordServiceResultProxy,
            )

            app.extensions["invenio-notifications"].entity_resolvers.setdefault(
                notification_resolver.type_key, notification_resolver
            )

        yield AddModule("finalize", exists_ok=True)
        yield AddToModule("finalize", "finalize_app", staticmethod(finalize_app))
        yield AddEntryPoint(
            group="invenio_base.finalize_app",
            name=f"{model.base_name}_requests",
            value="finalize:finalize_app",
            separator=".",
        )
        yield AddEntryPoint(
            group="invenio_base.api_finalize_app",
            name=f"{model.base_name}_requests",
            value="finalize:finalize_app",
            separator=".",
        )
