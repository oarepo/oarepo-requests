#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for registering resolvers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_drafts_resources.records import Draft
from invenio_rdm_records.records import RDMRecord, RDMDraft
from invenio_rdm_records.requests.entity_resolvers import RDMRecordServiceResultResolver, RDMRecordServiceResultProxy
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver, ServiceResultProxy
from oarepo_model.customizations import (
    AddEntryPoint,
    AddModule,
    AddToModule,
    Customization,
)
from oarepo_model.presets import Preset
from oarepo_runtime.services.results import RecordItem

if TYPE_CHECKING:
    from collections.abc import Generator

    from invenio_records_resources.references import RecordResolver
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel

class ServiceResultResolver(RDMRecordServiceResultResolver):
    """Service result resolver for draft records."""

    def __init__(self, service_id, type_key, proxy_cls=ServiceResultProxy, item_cls=None, record_cls=None):
        super(RDMRecordServiceResultResolver, self).__init__(service_id, type_key, proxy_cls, item_cls, record_cls)

"""        
class RDMRecordServiceResultResolver(ServiceResultResolver):


    def __init__(self):
        super().__init__(
            service_id=RDMRecordServiceConfig.service_id,
            type_key="record",
            proxy_cls=RDMRecordServiceResultProxy,
        )

    def _reference_entity(self, entity):
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}

    @property
    def draft_cls(self):
        return self.get_service().draft_cls

    def matches_entity(self, entity):
        if isinstance(entity, self.draft_cls):
            return True

        return ServiceResultResolver.matches_entity(self, entity=entity)
"""

class RegisterResolversPreset(Preset):
    """Preset for registering resolvers."""

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        def register_entity_resolver() -> RecordResolver:
            service_id = builder.model.base_name
            runtime_dependencies = builder.get_runtime_dependencies()
            resolver = runtime_dependencies.get("RecordResolver")
            return resolver(
                record_cls=runtime_dependencies.get("Record"),
                service_id=service_id,
                type_key=service_id,
                proxy_cls=runtime_dependencies.get("RecordProxy"),
            )

        def register_notification_resolver() -> ServiceResultResolver:
            service_id = builder.model.base_name
            return ServiceResultResolver(
                service_id=service_id,
                type_key=service_id,
                proxy_cls=RDMRecordServiceResultProxy,
            )

        register_notification_resolver.type_key = builder.model.base_name # just invenio things


        yield AddModule("resolvers", exists_ok=True)
        yield AddToModule("resolvers", "register_entity_resolver", staticmethod(register_entity_resolver))
        yield AddToModule("resolvers", "register_notification_resolver", staticmethod(register_notification_resolver))
        yield AddEntryPoint(
            group="invenio_requests.entity_resolvers",
            name=f"{model.base_name}_requests",
            value="resolvers:register_entity_resolver",
            separator=".",
        )
        yield AddEntryPoint(
            group="invenio_notifications.entity_resolvers",
            name=f"{model.base_name}_requests",
            value="resolvers:register_notification_resolver",
            separator=".",
        )
