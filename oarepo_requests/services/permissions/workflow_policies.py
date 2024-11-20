#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Permissions for requests based on workflows."""

from invenio_records_permissions.generators import SystemProcess
from invenio_requests.customizations.event_types import CommentEventType, LogEventType
from invenio_requests.services.generators import Creator, Receiver
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from oarepo_workflows.services.permissions import DefaultWorkflowPermissions

from oarepo_requests.services.permissions.generators.active import RequestActive
from oarepo_requests.services.permissions.generators.conditional import (
    IfEventType,
    IfRequestType,
)
from oarepo_requests.services.permissions.generators.workflow_based import (
    EventCreatorsFromWorkflow,
    RequestCreatorsFromWorkflow,
)


class RequestBasedWorkflowPermissions(DefaultWorkflowPermissions):
    """Base class for workflow permissions, subclass from it and put the result to Workflow constructor.

    This permission adds a special generator RequestActive() to the default permissions.
    Whenever the request is in `accept` action, the RequestActive generator matches.

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
    """Permissions for requests based on workflows.

    This permission adds a special generator RequestCreatorsFromWorkflow() to the default permissions.
    This generator takes a topic, gets the workflow from the topic and returns the generator for
    creators defined on the WorkflowRequest.
    """

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
