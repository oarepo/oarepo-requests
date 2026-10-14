# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Module providing preset for configuring requests result classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_model.customizations import (
    AddToList,
    Customization,
)
from oarepo_model.presets import Preset

from oarepo_requests.services.components.results import (
    RequestsComponent,
    RequestTypesComponent,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class RequestsRecordItemPreset(Preset):
    """Preset for configuring requests result classes."""

    modifies = ("record_result_item_components",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        yield AddToList("record_result_item_components", RequestsComponent)
        yield AddToList("record_result_item_components", RequestTypesComponent)
