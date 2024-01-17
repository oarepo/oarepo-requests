from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.proxies import current_request_type_registry

from oarepo_requests.errors import UnknownRequestType


class CreateRequestsService:
    def __init__(self, requests_service):
        self.requests_service = requests_service

    @unit_of_work()
    def create(
        self,
        identity,
        data,
        request_type,
        receiver,
        creator=None,
        topic=None,
        expires_at=None,
        uow=None,
        expand=False,
    ):
        type_ = current_request_type_registry.lookup(request_type, quiet=True)
        if not type_:
            raise UnknownRequestType(request_type)
        if hasattr(type_, "can_create"):
            error = type_.can_create(identity, data, receiver, topic, creator)
        else:
            error = None
        if not error:
            return self.requests_service.create(
                identity=identity,
                data=data,
                request_type=type_,
                receiver=receiver,
                creator=creator,
                topic=topic,
                expand=expand,
            )
