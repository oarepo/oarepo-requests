from invenio_records_resources.services.uow import unit_of_work
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
            receiver = current_oarepo_requests.default_request_receiver(request_type)
        if data is None:
            data = {}
        if hasattr(type_, "can_create"):
            error = type_.can_create(identity, data, receiver, topic, creator)
        else:
            error = None
        if not error:
            return super().create(
                identity=identity,
                data=data,
                request_type=type_,
                receiver=receiver,
                creator=creator,
                topic=topic,
                expand=expand,
                uow=uow,
            )

    def read(self, identity, id_, expand=False):
        api_request = super().read(identity, id_, expand)
        return api_request
