#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from flask_resources.serializers.base import MarshmallowSerializer
from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent

if TYPE_CHECKING:
    from collections.abc import Mapping


class ModelUIResourceConfig(RecordsUIResourceConfig):
    """Mock UI resource config."""

    model_name = "requests-test"

    api_service = "requests-test"  # must be something included in oarepo, as oarepo is used in tests

    blueprint_name = "requests_test"
    url_prefix = "/requests-test"
    ui_serializer_class = MarshmallowSerializer

    templates: ClassVar[Mapping[str, str | None]] = {
        **RecordsUIResourceConfig.templates,
        "detail": "TestDetail",
        "search": "TestDetail",
        "edit": "TestEdit",
    }

    components = (BabelComponent, PermissionsComponent)


class ModelUIResource(RecordsUIResource):
    """Mock UI resource."""

    def _exportable_handlers(self) -> list:
        return []
