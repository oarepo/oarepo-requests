from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.customizations import RequestType
from invenio_requests.proxies import current_requests_service

from oarepo_requests.errors import OpenRequestAlreadyExists
from oarepo_requests.utils import open_or_created_request_exists

from ..actions.generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from .ref_types import ModelRefTypes, ReceiverRefTypes


class OARepoRequestType(RequestType):
    description = None

    dangerous = False
    editable = True
    @classmethod
    @property
    def has_form(cls):
        return hasattr(cls, 'form')

    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        current_requests_service.require_permission(
            identity, "create", record=topic, request_type=self, **kwargs
        )

    @classmethod
    def is_applicable_to(cls, identity, topic, *args, **kwargs):
        """
        used for checking whether there is any situation where the client can create a request of this type
        it's different to just using can create with no receiver and data because that checks specifically
        for situation without them while this method is used to check whether there is a possible situation
        a user might create this request
        eg. for the purpose of serializing a link on associated record
        """
        try:
            current_requests_service.require_permission(
                identity, "create", record=topic, request_type=cls, **kwargs
            )
        except PermissionDeniedError:
            return False
        return True

    allowed_topic_ref_types = ModelRefTypes()
    allowed_receiver_ref_types = ReceiverRefTypes()

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "submit": OARepoSubmitAction,
            "accept": OARepoAcceptAction,
            "decline": OARepoDeclineAction,
        }

    def stateful_name(self, identity, request):
        """
        Returns the name of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        """
        return self.name

    def stateful_description(self, identity, request):
        """
        Returns the description of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        """
        return self.description


# can be simulated by switching state to a one which does not allow create
class NonDuplicableOARepoRequestType(OARepoRequestType):
    def can_create(self, identity, data, receiver, topic, creator, *args, **kwargs):
        if open_or_created_request_exists(topic, self.type_id):
            raise OpenRequestAlreadyExists(self, topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    @classmethod
    def is_applicable_to(cls, identity, topic, *args, **kwargs):
        if open_or_created_request_exists(topic, cls.type_id):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)
