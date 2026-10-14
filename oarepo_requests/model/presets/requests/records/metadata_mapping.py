# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Module to add requests-relevant metadata mappings on record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_model.customizations import Customization, PatchJSONFile
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from collections.abc import Generator

    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class RequestsMetadataMappingPreset(Preset):
    """Preset for applying requests-related record mapping changes."""

    modifies = ("record-mapping",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        yield PatchJSONFile(
            "record-mapping",
            {
                "mappings": {
                    "properties": {
                        "metadata": {
                            "properties": {
                                "version": {"type": "keyword"},
                            },
                        },
                    },
                },
            },
        )
