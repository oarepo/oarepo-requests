#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from oarepo_model.customizations import (
    AddMixins,
    AddToList,
    Customization,
)
from oarepo_model.model import InvenioModel, ModelMixin
from oarepo_model.presets import Preset

"""Module providing preset for processing request queries extension."""
if TYPE_CHECKING:
    from collections.abc import Generator

    from flask import Flask
    from oarepo_model.builder import InvenioModelBuilder

from invenio_rdm_records.requests.entity_resolvers import RDMRecordServiceResultProxy

from oarepo_requests.model.presets.requests.records.entity_resolvers.draft_resolver import WithDeletedServiceResultProxy
from oarepo_requests.proxies import current_oarepo_requests_service
from oarepo_requests.resolvers.service_result import DraftServiceResultResolver
from oarepo_requests.resources.draft.config import DraftRecordRequestsResourceConfig
from oarepo_requests.resources.draft.resource import DraftRecordRequestsResource
from oarepo_requests.services.draft.service import DraftRecordRequestsService

if TYPE_CHECKING:
    from oarepo_model.builder import InvenioModelBuilder

from invenio_records_resources.references.entity_resolvers.results import (
    ServiceResultResolver,
)


class RDMPIDServiceResultResolver(ServiceResultResolver):
    """Service result resolver for draft records."""

    def _reference_entity(self, entity):
        """Create a reference dict for the given result item."""
        pid = entity.id if isinstance(entity, self.item_cls) else entity.pid.pid_value
        return {self.type_key: str(pid)}


# ThesisFileDraftResolver(
#    record_cls=ThesisFileDraft,
#    service_id="thesis_file_draft",
#    type_key="thesis_file_draft",
# ),

"""
# todo ? the endpoint adding code could be automated on higher level? - it's just a bunch of copy paste
# decorators, yields seem to be a problem?

def create_endpoint_ext_class(name: str):
    capitalized_name = name.capitalize()
    return type(f"Ext{capitalized_name}Preset", (Preset,), {"name": name, f"{name}_service": })

class EndpointExtClassFactory(Preset):

    modifies = [
        "Ext",
    ]


    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization, None, None]:
        class ExtFilesMixin(ModelMixin):


            @cached_property
            def files_service(self):
                return self.get_model_dependency(f"{self.name}Service")(
                    **self.files_service_params,
                )

            @property

                return {
                    "config": build_config(
                        self.get_model_dependency(f"{self.name}ServiceConfig"), self.app
                    )
                }

            @cached_property
            def files_resource(self):
                return self.get_model_dependency(f"{self.name}Resource")(
                    **self.files_resource_params,
                )

            @property
            def files_resource_params(self):

                return {
                    "service": self.files_service,
                    "config": build_config(
                        self.get_model_dependency(f"{self.name}ResourceConfig"), self.app
                    ),
                }

        yield AddMixins("Ext", ExtFilesMixin)

        yield AddToList(
            "services_registry_list",
            (
                lambda ext: ext.files_service,
                lambda ext: ext.files_service.config.service_id,
            ),
        )
"""


class ExtRequestsPreset(Preset):
    """Preset for extension class."""

    depends_on = ["RecordResolver", "DraftResolver"]

    modifies = [
        "Ext",
    ]

    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        class ExtRequestsMixin(ModelMixin):
            """Mixin for extension class."""

            def init_config(self, app: Flask) -> None:
                """Initialize configuration."""
                service_id = builder.model.base_name
                type_key_published = service_id
                type_key_draft = f"{service_id}_draft"

                NOTIFICATIONS_ENTITY_RESOLVERS = [
                    RDMPIDServiceResultResolver(
                        service_id=service_id, type_key=type_key_published, proxy_cls=WithDeletedServiceResultProxy
                    ),
                    DraftServiceResultResolver(
                        service_id=service_id,
                        type_key=type_key_draft,
                        proxy_cls=RDMRecordServiceResultProxy,
                    ),
                ]

                app.config.setdefault("NOTIFICATIONS_ENTITY_RESOLVERS", [])
                app.config["NOTIFICATIONS_ENTITY_RESOLVERS"] += NOTIFICATIONS_ENTITY_RESOLVERS
                super().init_config(app)

            @cached_property
            def service_record_requests(self):
                return DraftRecordRequestsService(
                    **self.service_record_requests_params,
                )

            @property
            def service_record_requests_params(self):
                """Parameters for the file service."""
                return {
                    "record_service": self.records_service,
                    "oarepo_requests_service": current_oarepo_requests_service,
                }

            @cached_property
            def resource_record_requests(self):
                return DraftRecordRequestsResource(
                    **self.resource_record_requests_params,
                )

            @property
            def resource_record_requests_params(self):
                """Parameters for the file resource."""
                return {
                    "service": self.service_record_requests,
                    "config": self.records_resource.config,
                    "record_requests_config": DraftRecordRequestsResourceConfig(),
                }

        yield AddMixins("Ext", ExtRequestsMixin)

        yield AddToList(
            "services_registry_list",
            (
                lambda ext: ext.service_record_requests,
                lambda ext: ext.service_record_requests.config.service_id,
            ),
        )
