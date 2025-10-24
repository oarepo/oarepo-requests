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

from oarepo_model.customizations import (
    AddEntryPoint,
    AddModule,
    AddToModule,
    Customization,
)
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from collections.abc import Generator

    from invenio_records_resources.references import RecordResolver
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


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

        yield AddModule("resolvers", exists_ok=True)
        yield AddToModule("resolvers", "register_entity_resolver", staticmethod(register_entity_resolver))
        yield AddEntryPoint(
            group="invenio_requests.entity_resolvers",
            name=f"{model.base_name}_requests",
            value="resolvers:register_entity_resolver",
            separator=".",
        )
