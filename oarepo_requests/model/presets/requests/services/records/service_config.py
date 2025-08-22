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
from oarepo_requests.services.components.autorequest import AutorequestComponent
from invenio_drafts_resources.services import (
    RecordServiceConfig as DraftServiceConfig,
)
from invenio_records_resources.services import (
    ConditionalLink,
    RecordLink,
)
from invenio_records_resources.services.records.config import (
    RecordServiceConfig,
)
from oarepo_runtime.services.config import (
    has_draft,
    has_draft_permission,
    has_permission,
    has_published_record,
    is_published_record,
)

from oarepo_model.customizations import (
    AddMixins,
    AddToDictionary,
    AddToList,
    ChangeBase,
    Customization,
)
from oarepo_model.model import Dependency, InvenioModel, ModelMixin
from oarepo_model.presets import Preset

if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder

class RequestsServiceConfigPreset(Preset):
    """
    Preset for record service config class.
    """

    modifies = [
        "record_links_item",
        "record_service_components"
    ]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization, None, None]:

        api_base = "{+api}/" + builder.model.slug + "/"
        ui_base = "{+ui}/" + builder.model.slug + "/"

        api_url = api_base + "{id}"
        ui_url = ui_base + "{id}"

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

        yield AddToDictionary(
            "record_links_item",
            links
        )

        yield AddToList("record_service_components", AutorequestComponent)

