# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Module providing preset for applying changes to record service config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_model.customizations import (
    AddToDictionary,
    Customization,
)
from oarepo_model.presets import Preset

from oarepo_requests.services.links import RefEndpointLink

if TYPE_CHECKING:
    from collections.abc import Generator

    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class RequestsServiceConfigPreset(Preset):
    """Preset for record service config class."""

    modifies = ("record_links_item", "record_service_components")

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        # TODO: AutorequestComponent, RecordSnapshotComponent
        yield AddToDictionary(
            "record_links_item",
            {"requests": RefEndpointLink("requests.search", ref_querystring="topic")},
        )
        yield AddToDictionary(
            "record_links_item",
            {"applicable-requests": RefEndpointLink("requests.applicable_request_types", ref_querystring="topic")},
        )
