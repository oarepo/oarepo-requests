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
from functools import cached_property
from typing import TYPE_CHECKING, Any

from oarepo_model.customizations import (
    AddMixins,
    AddToList,
    Customization,
)
from oarepo_model.model import InvenioModel, ModelMixin
from oarepo_model.presets import Preset

from oarepo_requests.proxies import current_oarepo_requests_service
from oarepo_requests.resources.draft.types.config import DraftRequestTypesResourceConfig
from oarepo_requests.resources.draft.types.resource import DraftRequestTypesResource
from oarepo_requests.services.draft.types.service import DraftRecordRequestTypesService

"""Module providing preset for processing request types queries extension."""
if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder


class ExtRequestTypesPreset(Preset):
    """Preset for extension class."""

    depends_on = ["RecordService", "RecordServiceConfig"]
    modifies = ["Ext"]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class ExtRequestTypesMixin(ModelMixin):
            """Mixin for extension class."""

            @cached_property
            def service_record_request_types(self):
                return DraftRecordRequestTypesService(
                    **self.service_record_request_types_params,
                )

            @property
            def service_record_request_types_params(self):
                """Parameters for the file service."""
                return {
                    "record_service": self.records_service,
                    "oarepo_requests_service": current_oarepo_requests_service,
                }

            @cached_property
            def resource_record_request_types(self):
                return DraftRequestTypesResource(
                    **self.resource_record_request_types_params,
                )

            @property
            def resource_record_request_types_params(self):
                """Parameters for the file resource."""
                return {
                    "service": self.service_record_request_types,
                    "config": self.records_resource.config,
                    "record_requests_config": DraftRequestTypesResourceConfig(),
                }

        yield AddMixins("Ext", ExtRequestTypesMixin)

        yield AddToList(
            "services_registry_list",
            (
                lambda ext: ext.service_record_request_types,
                lambda ext: ext.service_record_request_types.config.service_id,
            ),
        )
