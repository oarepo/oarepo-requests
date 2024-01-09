from invenio_requests.customizations import RequestType
from invenio_requests.proxies import current_requests_service

from oarepo_requests.actions.delete_topic import DeleteTopicAcceptAction
from oarepo_requests.errors import OpenRequestAlreadyExists
from oarepo_requests.utils import open_request_exists, resolve_reference_dict
from invenio_records_resources.services.errors import PermissionDeniedError


class OARepoRequestType(RequestType):

    def can_create(
        self, identity, data, receiver, topic, creator, *args, **kwargs
    ):
        current_requests_service.require_permission(identity, "create")
    @classmethod
    def can_possibly_create(
        self, identity, topic, *args, **kwargs
    ):
        """
        used for checking whether there is any situation where the client can create a request of this type
        it's different to just using can create with no receiver and data because that checks specifically
        for situation without them while this method is used to check whether there is a possible situation
        a user might create this request
        eg. for the purpose of serializing a link on associated record
        """
        try:
            current_requests_service.require_permission(identity, "create")
        except PermissionDeniedError:
            return False
        return True
