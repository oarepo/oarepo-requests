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
    Customization, AddToDictionary,
)
from oarepo_model.presets import Preset
from oarepo_runtime.services.config import is_published_record

from oarepo_requests.services.components.autorequest import AutorequestComponent
from oarepo_requests.services.record.components.snapshot_component import (
    RecordSnapshotComponent,
)
from invenio_records_resources.services.base.links import EndpointLink
from invenio_records_resources.services.records.links import RecordEndpointLink
from invenio_records_resources.services.base.links import ConditionalLink
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
        yield AddToDictionary(
            "record_links_item",
            {
                "requests": ConditionalLink(
                    cond=is_published_record(),
                    if_=RecordEndpointLink(
                    f"{builder.model.base_name}_requests.search_requests_for_record", # TODO: how to get the blueprint name correctly?
                ),
                    else_=RecordEndpointLink(
                    f"{builder.model.base_name}_requests.search_requests_for_draft",
                )
                )
            }
        )
        yield AddToDictionary(
            "record_links_item",
            {
                "applicable-requests": ConditionalLink(
                    cond=is_published_record(),
                    if_=RecordEndpointLink(
                    f"{builder.model.base_name}_applicable_requests.get_applicable_request_types", # TODO: how to get the blueprint name correctly?
                ),
                    else_=RecordEndpointLink(
                    f"{builder.model.base_name}_applicable_requests.get_applicable_request_types_for_draft",
                )
                )
            }
        )
