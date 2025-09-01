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
from typing import TYPE_CHECKING, Any

from oarepo_model.customizations import (
    AddClass,
    AddMixins,
    Customization,
)
from oarepo_model.model import InvenioModel
from oarepo_model.presets import Preset

from oarepo_requests.model.presets.requests.records.entity_resolvers.draft_resolver import RecordProxy

if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder


"""
{{ vars.record_resolver|generate_import }}
{% if vars.record_resolver.custom_proxy_class %}
{{ vars.record_resolver.custom_proxy_class|generate_import }}
{% endif %}

class {{ vars.record_resolver|class_header }}:
    # invenio_requests.registry.TypeRegistry
    # requires name of the resolver for the model; needs only to be unique for the model, so use the name of the model
    type_id = "{{ vars.module.prefix_snake }}"
{% if vars.record_resolver.custom_proxy_class %}
    proxy_cls = {{ vars.record_resolver.custom_proxy_class|base_name }}
    def __init__(
        self, record_cls, service_id, type_key
    ):
        super().__init__(record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls)
{% endif %}
"""

# TODO: temp
from invenio_records_resources.references import RecordResolver


class RecordResolverPreset(Preset):
    provides = [
        "RecordResolver",
    ]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class RecordResolverMixin:
            """Base class for records in the model.
            This class extends InvenioRecord and can be customized further.
            """

            # invenio_requests.registry.TypeRegistry
            # requires name of the resolver for the model; needs only to be unique for the model, so use the name of the model
            type_id = builder.model.base_name

            proxy_cls = RecordProxy

            def __init__(self, record_cls, service_id, type_key):
                super().__init__(record_cls, service_id, type_key=type_key, proxy_cls=self.proxy_cls)

        yield AddClass(
            "RecordResolver",
            clazz=RecordResolver,
        )
        yield AddMixins(
            "RecordResolver",
            RecordResolverMixin,
        )
