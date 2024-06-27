from invenio_requests import current_request_type_registry
from invenio_access.permissions import SystemRoleNeed

from ..errors import OpenRequestAlreadyExists
from ..proxies import current_oarepo_requests, current_oarepo_requests_service
from invenio_requests.proxies import current_requests_service
from invenio_records_resources.services.errors import PermissionDeniedError
import copy
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_records_resources.services.uow import (
    unit_of_work,
)

from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError

from flask_principal import AnonymousIdentity

autorequest = SystemRoleNeed("autorequest")
from invenio_records_permissions.generators import Generator
from invenio_access.factory import action_factory
class RequestAction(Generator):
    """Generator for admin needs.

    This generator's purpose is to be used in cases where administration needs are required.
    The query filter of this generator is quite broad (match_all). Therefore, it must be used with care.
    """

    def __init__(self, request_action):
        """Constructor."""
        self.request_action = action_factory(request_action)
        super().__init__()

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [self.request_action]
@unit_of_work()
def auto_requester(identity, record, prev_value, next_value, *args, uow=None, **kwargs):
    identity_copy = AnonymousIdentity()
    identity_copy.provides.add(autorequest)
    creator = ResolverRegistry.reference_identity(identity)
    for request_type in current_request_type_registry:
        data = kwargs["data"] if "data" in kwargs else None
        #identity_copy = copy.deepcopy(identity)
        #identity_copy.provides |= set(RequestAction(request_type.type_id).needs())
        # todo discuss this; using action need - i requires saving some mapping to db
        try:
            request_item = current_oarepo_requests_service.create(identity_copy, data=data, request_type=request_type.type_id, topic=record, creator=creator, uow=uow, *args, **kwargs)
            action_obj = RequestActions.get_action(request_item._record, "submit")
            if not action_obj.can_execute():
                raise CannotExecuteActionError("submit")
            action_obj.execute(identity, uow)
        # todo better exception catching
        except Exception:
            pass