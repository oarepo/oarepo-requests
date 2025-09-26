#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo extension to invenio-requests service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_i18n import _
from invenio_records_resources.services.uow import IndexRefreshOp, unit_of_work
from invenio_requests import current_request_type_registry
from invenio_requests.services import RequestsService

from oarepo_requests.errors import CustomHTTPJSONException, UnknownRequestTypeError
from oarepo_requests.proxies import current_oarepo_requests
from invenio_records_resources.services.base.links import EndpointLink
from oarepo_requests.utils import allowed_request_types_for_record, resolve_reference_dict
from oarepo_requests.services.results import RequestTypesList, DraftAwareEntityResolverExpandableField, \
    StringDraftAwareEntityResolverExpandableField
from invenio_records_resources.services import LinksTemplate
from invenio_drafts_resources.records.api import Record
from invenio_requests.services.results import EntityResolverExpandableField

if TYPE_CHECKING:
    from datetime import datetime

    from flask_principal import Identity
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.services.requests.results import RequestItem

    from oarepo_requests.typing import EntityReference


class OARepoRequestsService(RequestsService):
    """OARepo extension to invenio-requests service."""

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return [
            EntityResolverExpandableField("created_by"),
            EntityResolverExpandableField("receiver"),
            DraftAwareEntityResolverExpandableField("topic"),
            StringDraftAwareEntityResolverExpandableField("payload.created_topic"),
        ]

    @unit_of_work()
    def create(  # noqa: PLR0913
        self,
        identity: Identity,
        data: dict,
        request_type: str,
        receiver: EntityReference | Any | None = None,
        creator: EntityReference | Any | None = None,
        topic: Record = None,
        expires_at: datetime | None = None,  # noqa ARG002
        uow: UnitOfWork = None,
        expand: bool = False,
        *args: Any,  # noqa ARG002
        **kwargs: Any,  # noqa ARG002
    ) -> RequestItem:
        """Create a request.

        :param identity: Identity of the user creating the request.
        :param data: Data of the request.
        :param request_type: Type of the request.
        :param receiver: Receiver of the request. If unfilled, a default receiver from workflow is used.
        :param creator: Creator of the request.
        :param topic: Topic of the request.
        :param expires_at: Expiration date of the request.
        :param uow: Unit of work.
        :param expand: Expand the response.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """
        type_ = current_request_type_registry.lookup(request_type, quiet=True)
        if not type_:
            raise UnknownRequestTypeError(request_type)

        if receiver is None:
            # if explicit creator is not passed, use current identity - this is in sync with invenio_requests
            receiver = current_oarepo_requests.default_request_receiver(
                identity, type_, topic, creator or identity, data
            )

        if data is None:
            data = {}
        if "payload" not in data and type_.payload_schema:
            data["payload"] = {}
        schema = self._wrap_schema(type_.marshmallow_schema())
        data, errors = schema.load(
            data,
            context={"identity": identity},
            raise_errors=False,
        )
        if errors:
            raise CustomHTTPJSONException(
                description=_(
                    "Action could not be performed due to validation request fields validation errors."
                ),
                request_payload_errors=errors,
                code=400,
            )

        error = (
            type_.can_create(identity, data, receiver, topic, creator)
            if hasattr(type_, "can_create")
            else None
        )

        if not error:
            result = super().create(
                identity=identity,
                data=data,
                request_type=type_,
                receiver=receiver,
                creator=creator,
                topic=topic,
                expand=expand,
                uow=uow,
            )
            uow.register(
                IndexRefreshOp(indexer=self.indexer, index=self.record_cls.index)
            )
            return result
        return None

    def applicable_request_types(
        self, identity: Identity, topic: Record | EntityReference
    ) -> RequestTypesList:
        """Get applicable request types for a record."""
        topic = (
            resolve_reference_dict(topic)
            if not isinstance(topic, Record)
            else topic
        )  # type: ignore if isinstance(record, Record) else record

        allowed_request_types = allowed_request_types_for_record(identity, topic)
        return RequestTypesList(
            service=self,  # TODO: unserious
            identity=identity,
            results=list(allowed_request_types.values()),
            links_tpl=LinksTemplate(
                {"self": EndpointLink("oarepo_requests.applicable_request_types")}
            ),
            record=topic,
        )
