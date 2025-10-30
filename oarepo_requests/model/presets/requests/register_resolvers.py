#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-model (see http://github.com/oarepo/oarepo-model).
#
# oarepo-model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Module providing preset for registering resolvers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_access.permissions import system_identity
from invenio_drafts_resources.services import RecordService as RecordServiceWithDrafts
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.requests.entity_resolvers import RDMRecordServiceResultProxy, RDMRecordServiceResultResolver
from oarepo_model.customizations import (
    AddEntryPoint,
    AddModule,
    AddToModule,
    Customization,
)
from oarepo_model.presets import Preset
from oarepo_runtime.typing import record_from_result
from sqlalchemy.exc import NoResultFound

if TYPE_CHECKING:
    from collections.abc import Generator

    from invenio_drafts_resources.records import Draft
    from invenio_records_resources.records import Record
    from invenio_records_resources.references import RecordResolver
    from invenio_records_resources.services.records.results import RecordItem
    from oarepo_model.builder import InvenioModelBuilder
    from oarepo_model.model import InvenioModel


class ServiceResultProxy(RDMRecordServiceResultProxy):
    """Proxy to resolve a record service result."""

    @override
    def _resolve(self) -> dict[str, Any]:
        """Resolve the result item from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()
        if isinstance(self.service, RecordServiceWithDrafts):
            try:
                draft = self.service.read_draft(system_identity, pid_value)
            except (PIDDoesNotExistError, NoResultFound):
                record = self._get_record(pid_value)
            else:
                # no exception raised. If published, get the published record instead
                # Difference between is_published and publication_status?
                record = (
                    draft if record_from_result(draft).publication_status == "draft" else self._get_record(pid_value)  # type: ignore[reportAttributeAccessIssue]
                )
        else:
            record = self._get_record(pid_value)

        return record.to_dict()  # type: ignore[no-any-return]


class ServiceResultResolver(RDMRecordServiceResultResolver):
    """Service result resolver for draft records."""

    def __init__(
        self,
        service_id: str,
        type_key: str,
        proxy_cls: type[ServiceResultProxy] = ServiceResultProxy,
        item_cls: type[RecordItem] | None = None,
        record_cls: type[Record] | None = None,
    ):
        """Initialize the resolver."""
        super(RDMRecordServiceResultResolver, self).__init__(service_id, type_key, proxy_cls, item_cls, record_cls)

    @property
    @override
    def draft_cls(self) -> type[Draft] | None:
        """Get specified draft class or from service."""
        service = self.get_service()
        return service.draft_cls if isinstance(service, RecordServiceWithDrafts) else None

    @override
    def matches_entity(self, entity: Any) -> bool:
        """Check if the entity is a draft."""
        if self.draft_cls and isinstance(entity, self.draft_cls):
            return True

        return ServiceResultResolver.matches_entity(self, entity=entity)


class RegisterResolversPreset(Preset):
    """Preset for registering resolvers."""

    @override
    def apply(
        self,
        builder: InvenioModelBuilder,
        model: InvenioModel,
        dependencies: dict[str, Any],
    ) -> Generator[Customization]:
        def register_entity_resolver() -> RecordResolver:
            service_id = builder.model.base_name
            runtime_dependencies = builder.get_runtime_dependencies()
            resolver = runtime_dependencies.get("RecordResolver")
            return resolver(
                record_cls=runtime_dependencies.get("Record"),
                service_id=service_id,
                type_key=service_id,
                proxy_cls=runtime_dependencies.get("RecordProxy"),
            )

        def register_notification_resolver() -> ServiceResultResolver:
            service_id = builder.model.base_name
            return ServiceResultResolver(
                service_id=service_id,
                type_key=service_id,
                proxy_cls=ServiceResultProxy,
            )

        # just invenio things
        register_notification_resolver.type_key = builder.model.base_name  # type: ignore[attr-defined]

        yield AddModule("resolvers", exists_ok=True)
        yield AddToModule("resolvers", "register_entity_resolver", staticmethod(register_entity_resolver))
        yield AddToModule("resolvers", "register_notification_resolver", staticmethod(register_notification_resolver))
        yield AddEntryPoint(
            group="invenio_requests.entity_resolvers",
            name=f"{model.base_name}_requests",
            value="resolvers:register_entity_resolver",
            separator=".",
        )
        yield AddEntryPoint(
            group="invenio_notifications.entity_resolvers",
            name=f"{model.base_name}_requests",
            value="resolvers:register_notification_resolver",
            separator=".",
        )
