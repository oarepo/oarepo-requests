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

    from flask import Flask
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class RequestsFinalizeAppPreset(Preset):
    """Preset for extension class."""

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        def finalize_app(app: Flask) -> None:
            # TODO: ask about depends on
            runtime_deps = builder.get_runtime_dependencies()
            service_id = builder.model.base_name
            REQUESTS_ENTITY_RESOLVERS = [
                runtime_deps.get("RecordResolver")(
                    record_cls=runtime_deps.get("Record"),
                    draft_cls=runtime_deps.get("Draft"),
                    service_id=service_id,
                    type_key=service_id,
                ),
            ]
            requests = app.extensions["invenio-requests"]
            for resolver in REQUESTS_ENTITY_RESOLVERS:
                requests.entity_resolvers_registry.register_type(resolver)

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
