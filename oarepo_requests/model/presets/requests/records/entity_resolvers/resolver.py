#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for draft entity resolver creation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

# TODO: temp
from invenio_records_resources.references import RecordResolver as InvenioRecordResolver
from oarepo_model.customizations import (
    AddClass,
    AddMixins,
    Customization,
)
from oarepo_model.presets import Preset

from oarepo_requests.model.presets.requests.records.entity_resolvers.draft_resolver import (
    RecordProxy,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from invenio_records_resources.references import RecordResolver
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel
else:
    RecordResolver = object


class RecordResolverPreset(Preset):
    """Preset for published resolver."""

    provides = ("RecordResolver",)

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class RecordResolverMixin(RecordResolver):
            """Mixin specifying published record resolver."""

            # requires name of the resolver for the model; needs only to be unique for the model,
            # so use the name of the model
            type_id = builder.model.base_name

            proxy_cls = RecordProxy

            def __init__(self, record_cls: type, service_id: str, type_key: str) -> None:
                """Construct the resolver."""
                super().__init__(record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls)

        yield AddClass(
            "RecordResolver",
            clazz=InvenioRecordResolver,
        )
        yield AddMixins(
            "RecordResolver",
            RecordResolverMixin,
        )
