from invenio_records_resources.services.uow import IndexRefreshOp, unit_of_work
from invenio_requests import current_request_type_registry
from invenio_requests.services import RequestsService

from oarepo_requests.errors import UnknownRequestType
from oarepo_requests.proxies import current_oarepo_requests


class OARepoRequestsService(RequestsService):
    @unit_of_work()
    def create(
        self,
        identity,
        data,
        request_type,
        receiver=None,
        creator=None,
        topic=None,
        expires_at=None,
        uow=None,
        expand=False,
    ):
        type_ = current_request_type_registry.lookup(request_type, quiet=True)
        if not type_:
            raise UnknownRequestType(request_type)

        if receiver is None:
            receiver_getter = current_oarepo_requests.default_request_receiver(
                request_type
            )
            receiver = receiver_getter(identity, request_type, topic, creator)
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

    def read(self, identity, id_, expand=False):
        api_request = super().read(identity, id_, expand)
        return api_request

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None, expand=False):
        result = super().update(
            identity, id_, data, revision_id=revision_id, uow=uow, expand=expand
        )
        uow.register(IndexRefreshOp(indexer=self.indexer, index=self.record_cls.index))
        return result
