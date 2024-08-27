from invenio_records_permissions.generators import SystemProcess
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows import DefaultWorkflowPermissions

from oarepo_requests.services.permissions.generators import (
    CreatorsFromWorkflow,
    IfRequestType,
    RequestActive,
)


class RequestBasedWorkflowPermissions(DefaultWorkflowPermissions):
    """
    Base class for workflow permissions, subclass from it and put the result to Workflow constructor.
    Example:
        class MyWorkflowPermissions(RequestBasedWorkflowPermissions):
            can_read = [AnyUser()]
    in invenio.cfg
    WORKFLOWS = {
        'default': Workflow(
            permission_policy_cls = MyWorkflowPermissions, ...
        )
    }
    """
    can_delete = DefaultWorkflowPermissions.can_delete + [RequestActive()]
    can_publish = [RequestActive()]
    can_edit = [RequestActive()]
    can_new_version = [RequestActive()]


class CreatorsFromWorkflowRequestsPermissionPolicy(InvenioRequestsPermissionPolicy):
    can_create = [
        SystemProcess(),
        CreatorsFromWorkflow(),
        IfRequestType(
            ["community-invitation"], InvenioRequestsPermissionPolicy.can_create
        ),
    ]
