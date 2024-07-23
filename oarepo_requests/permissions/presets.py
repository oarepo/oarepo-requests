from invenio_records_permissions.generators import AnyUser, AuthenticatedUser
from oarepo_runtime.services.generators import RecordOwners
from oarepo_workflows import DefaultWorkflowPermissionPolicy, IfInState

from oarepo_requests.permissions.generators import RequestActive, RecordRequestsReceivers


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
