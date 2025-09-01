#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Any

from oarepo_model.customizations import (
    AddEntryPoint,
    AddModule,
    AddToModule,
    Customization,
)
from oarepo_model.model import InvenioModel
from oarepo_model.presets import Preset

"""Module providing preset for defining finalize_app entrypoints."""
if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder


# ThesisFileDraftResolver(
#    record_cls=ThesisFileDraft,
#    service_id="thesis_file_draft",
#    type_key="thesis_file_draft",
# ),


class RequestsFinalizeAppPreset(Preset):
    """Preset for extension class."""

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        @staticmethod
        def finalize_app(app):
            runtime_deps = builder.get_runtime_dependencies()
            service_id = builder.model.base_name
            type_key_published = service_id
            type_key_draft = f"{service_id}_draft"
            REQUESTS_ENTITY_RESOLVERS = [
                runtime_deps.get("RecordResolver")(
                    record_cls=runtime_deps.get("Record"), service_id=service_id, type_key=type_key_published
                ),
                runtime_deps.get("DraftResolver")(
                    record_cls=runtime_deps.get("Draft"), service_id=service_id, type_key=type_key_draft
                ),
            ]
            requests = app.extensions["invenio-requests"]
            for resolver in REQUESTS_ENTITY_RESOLVERS:
                requests.entity_resolvers_registry.register_type(resolver)

        yield AddModule("finalize", exists_ok=True)
        yield AddToModule("finalize", "finalize_app", finalize_app)
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
