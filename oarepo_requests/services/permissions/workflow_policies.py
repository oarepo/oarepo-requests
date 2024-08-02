from invenio_records_permissions.generators import SystemProcess
from invenio_requests.services.permissions import (
    PermissionPolicy as RequestsPermissionPolicy,
)
from oarepo_workflows import DefaultWorkflowPermissionPolicy

from oarepo_requests.services.permissions.generators import (
    CreatorsFromWorkflow,
    RequestActive,
)


class DefaultWithRequestsWorkflowPermissionPolicy(DefaultWorkflowPermissionPolicy):
    can_delete = DefaultWorkflowPermissionPolicy.can_delete + [RequestActive()]
    can_publish = [RequestActive()]
    can_edit = [RequestActive()]


class CreatorsFromWorkflowPermissionPolicy(RequestsPermissionPolicy):
    can_create = [
        SystemProcess(),
        CreatorsFromWorkflow(),
    ]
