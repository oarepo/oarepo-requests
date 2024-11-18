"""OARepo extension to invenio-requests service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_records_resources.services.uow import IndexRefreshOp, unit_of_work
from invenio_requests import current_request_type_registry
from invenio_requests.services import RequestsService

from oarepo_requests.errors import UnknownRequestType
from oarepo_requests.proxies import current_oarepo_requests

if TYPE_CHECKING:
    from datetime import datetime

    from flask_principal import Identity
    from invenio_records.api import RecordBase
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.services.requests.results import RequestItem


class OARepoRequestsService(RequestsService):
    """OARepo extension to invenio-requests service."""

    @unit_of_work()
    def create(
        self,
        identity: Identity,
        data: dict,
        request_type: str,
        receiver: dict[str, str] | Any | None = None,
        creator: dict[str, str] | Any | None = None,
        topic: RecordBase = None,
        expires_at: datetime | None = None,
        uow: UnitOfWork = None,
        expand: bool = False,
        *args: Any,
        **kwargs: Any,
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
            raise UnknownRequestType(request_type)

        if receiver is None:
            # if explicit creator is not passed, use current identity - this is in sync with invenio_requests
            receiver = current_oarepo_requests.default_request_receiver(
                identity, type_, topic, creator or identity, data
            )

        if data is None:
            data = {}

        if hasattr(type_, "can_create"):
            error = type_.can_create(identity, data, receiver, topic, creator)
        else:
            error = None

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

    @override
    def read(self, identity: Identity, id_: str, expand: bool = False) -> RequestItem:
        api_request = super().read(identity, id_, expand)
        return api_request

    @override
    @unit_of_work()
    def update(
        self,
        identity: Identity,
        id_: str,
        data: dict,
        revision_id: int | None = None,
        uow: UnitOfWork | None = None,
        expand: bool = False,
    ) -> RequestItem:
        result = super().update(
            identity, id_, data, revision_id=revision_id, uow=uow, expand=expand
        )
        uow.register(IndexRefreshOp(indexer=self.indexer, index=self.record_cls.index))
        return result
