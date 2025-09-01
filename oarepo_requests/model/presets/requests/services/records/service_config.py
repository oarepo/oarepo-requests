#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for applying changes to record service config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_model.customizations import (
    AddToList,
    Customization,
)
from oarepo_model.presets import Preset

from oarepo_requests.services.components.autorequest import AutorequestComponent
from oarepo_requests.services.record.components.snapshot_component import RecordSnapshotComponent

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
        yield AddToList("record_service_components", AutorequestComponent)
        yield AddToList("record_service_components", RecordSnapshotComponent)

        # TODO: use endpoint links
        """api_base = "{+api}/" + builder.model.slug + "/"
        ui_base = "{+ui}/" + builder.model.slug + "/"

        api_url = api_base + "{id}"
        ui_base + "{id}"

        links = {
            "requests": ConditionalLink(
                cond=is_published_record(),
                if_=RecordLink(api_url + "/requests"),
                else_=RecordLink(api_url + "/draft/requests"),
            ),
            "applicable-requests": ConditionalLink(
                cond=is_published_record(),
                if_=RecordLink(api_url + "/requests/applicable"),
                else_=RecordLink(api_url + "/draft/requests/applicable"),
            ),
        }


        yield AddToDictionary("record_links_item", links)
        """
