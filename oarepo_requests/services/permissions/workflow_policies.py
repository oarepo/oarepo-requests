from invenio_records_permissions.generators import SystemProcess
from invenio_requests.customizations.event_types import CommentEventType, LogEventType
from invenio_requests.services.generators import Creator, Receiver
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows import DefaultWorkflowPermissions

from oarepo_requests.services.permissions.generators import (
    EventCreatorsFromWorkflow,
    IfEventType,
    IfRequestType,
    RequestActive,
    RequestCreatorsFromWorkflow,
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
        RequestCreatorsFromWorkflow(),
        IfRequestType(
            ["community-invitation"], InvenioRequestsPermissionPolicy.can_create
        ),
    ]

    can_create_comment = [
        SystemProcess(),
        IfEventType(
            [LogEventType.type_id, CommentEventType.type_id], [Creator(), Receiver()]
        ),
        EventCreatorsFromWorkflow(),
    ]
