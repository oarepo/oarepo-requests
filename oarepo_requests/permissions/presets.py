from invenio_records_permissions.generators import AnyUser, AuthenticatedUser, SystemProcess
from oarepo_runtime.services.generators import RecordOwners
from oarepo_workflows import DefaultWorkflowPermissionPolicy, IfInState
from invenio_requests.services.permissions import PermissionPolicy

from oarepo_requests.permissions.generators import (
    RecordRequestsReceivers,
    RequestActive, CreatorsFromWorkflow,
)


class DefaultWithRequestsWorkflowPermissionPolicy(DefaultWorkflowPermissionPolicy):
    can_read = [
        AnyUser(),  # needed for ui tests, eventually change them or scrape
        AuthenticatedUser(),
        RecordRequestsReceivers(),
        #        IfInState("draft", [AuthenticatedUser(), RecordOwners()]),
        #        IfInState("publishing", [AuthenticatedUser(), RecordOwners()]), # todo - temporary, we need a way to make record accessible to request receiver
        #        IfInState("published", [AuthenticatedUser()]),
    ]

    can_delete = [
        IfInState("draft", [RecordOwners()]),
        IfInState("deleting", [RequestActive()]),
    ]

    can_publish = [RequestActive()]
    can_edit = [RequestActive()]

class CreatorsFromWorkflowPermissionPolicy(PermissionPolicy):
    can_create = [
        SystemProcess(),
        CreatorsFromWorkflow(),
    ]
