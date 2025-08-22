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
    Customization, AddEntryPoint, AddModule, AddToModule,
)
from oarepo_model.model import InvenioModel, Dependency
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder


# ThesisFileDraftResolver(
#    record_cls=ThesisFileDraft,
#    service_id="thesis_file_draft",
#    type_key="thesis_file_draft",
# ),


class RequestsFinalizeAppPreset(Preset):
    """
    Preset for extension class.
    """
    depends_on = ["RecordResolver", "DraftResolver"]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization, None, None]:

        @staticmethod
        def finalize_app(app):
            runtime_deps = builder.get_runtime_dependencies()
            ENTITY_RESOLVERS = [
                runtime_deps.get("RecordResolver")(record_cls=runtime_deps.get("Record"), service_id=builder.model.base_name, type_key=builder.model.base_name),
                runtime_deps.get("DraftResolver")(record_cls=runtime_deps.get("Draft"), service_id=builder.model.base_name, type_key=f"{builder.model.base_name}_draft"),
            ]
            requests = app.extensions["invenio-requests"]
            for resolver in ENTITY_RESOLVERS:
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