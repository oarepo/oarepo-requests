from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from invenio_requests.proxies import current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.services.permissions.identity import auto_request_need

from oarepo_requests.proxies import current_oarepo_requests_service


@unit_of_work()
def auto_request_state_change_notifier(
    identity, record, prev_value, value, uow=None, **kwargs
):
    for request_type_id, workflow_request in (
        current_oarepo_workflows.get_workflow(record).requests().items()
    ):
        needs = workflow_request.needs(
            request_type=request_type_id, record=record, **kwargs
        )
        if auto_request_need in needs:
            data = kwargs["data"] if "data" in kwargs else {}
            creator_ref = ResolverRegistry.reference_identity(identity)
            request_item = current_oarepo_requests_service.create(
                system_identity,
                data=data,
                request_type=request_type_id,
                topic=record,
                creator=creator_ref,
                uow=uow,
                **kwargs,
            )
            action_obj = RequestActions.get_action(request_item._record, "submit")
            if not action_obj.can_execute():
                raise CannotExecuteActionError("submit")
            action_obj.execute(identity, uow)
            uow.register(
                RecordCommitOp(
                    request_item._record, indexer=current_requests_service.indexer
                )
            )
