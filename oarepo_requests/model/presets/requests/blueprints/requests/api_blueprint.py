#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_model.customizations import (
    AddEntryPoint,
    AddToModule,
    Customization,
)
from oarepo_model.presets import Preset

"""API blueprint preset for api requests query on record."""
if TYPE_CHECKING:
    from collections.abc import Generator

    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class ApiRequestsBlueprintPreset(Preset):
    """Preset for api blueprint."""

    modifies = ["blueprints"]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        @staticmethod  # need to use staticmethod as python's magic always passes self as the first argument
        def create_requests_api_blueprint(app):
            with app.app_context():
                return app.extensions[model.base_name].resource_record_requests.as_blueprint()


        yield AddToModule(
            "blueprints",
            "create_requests_api_blueprint",
            create_requests_api_blueprint,
        )

        yield AddEntryPoint(
            group="invenio_base.api_blueprints",
            name=f"{model.base_name}_requests",
            value="blueprints:create_requests_api_blueprint",
            separator=".",
        )
