from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_requests.services.permissions import PermissionPolicy
from oarepo_runtime.services.generators import RecordOwners
from oarepo_workflows import DefaultWorkflowPermissionPolicy, IfInState

from oarepo_requests.permissions.generators import (
    CreatorsFromWorkflow,
    RecordRequestsReceivers,
    RequestActive,
)


class DefaultWithRequestsWorkflowPermissionPolicy(DefaultWorkflowPermissionPolicy):
    can_read = [
        IfInState("draft", [RecordOwners()]),
        IfInState("publishing", [RecordOwners(), RecordRequestsReceivers()]),
        IfInState("published", [AnyUser()]),
        IfInState("deleting", [AnyUser()]),
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
