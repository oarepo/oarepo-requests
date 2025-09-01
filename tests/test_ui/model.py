#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent
from thesis.resources.records.ui import ThesisUIJSONSerializer


class ModelUIResourceConfig(RecordsUIResourceConfig):
    api_service = "thesis"  # must be something included in oarepo, as oarepo is used in tests

    blueprint_name = "thesis"
    url_prefix = "/thesis/"
    ui_serializer_class = ThesisUIJSONSerializer

    templates = {
        **RecordsUIResourceConfig.templates,
        "detail": "TestDetail",
        "search": "TestDetail",
        "edit": "TestEdit",
    }

    components = [BabelComponent, PermissionsComponent]


class ModelUIResource(RecordsUIResource):
    def _exportable_handlers(self):
        return []
