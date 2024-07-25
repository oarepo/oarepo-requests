from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests import current_request_type_registry
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from invenio_requests.resolvers.registry import ResolverRegistry
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.requests.policy import auto_request_need

from ..proxies import current_oarepo_requests_service
from ..utils import get_from_requests_workflow

# todo - move possibly
@unit_of_work()
def auto_requester(identity, record, prev_value, value, *args, uow=None, **kwargs):
    workflow_id = current_oarepo_workflows.get_workflow_from_record(record)
    for request_type in current_request_type_registry:
        creators = get_from_requests_workflow(
            workflow_id, request_type.type_id, "requesters"
        )
        for generator in creators:
            needs = generator.needs(record=record, **kwargs)
            if auto_request_need in needs:
                data = kwargs["data"] if "data" in kwargs else None
                creator_ref = ResolverRegistry.reference_identity(identity)
                request_item = current_oarepo_requests_service.create(
                    system_identity,
                    data=data,
                    request_type=request_type.type_id,
                    topic=record,
                    creator=creator_ref,
                    uow=uow,
                    *args,
                    **kwargs,
                )
                action_obj = RequestActions.get_action(request_item._record, "submit")
                if not action_obj.can_execute():
                    raise CannotExecuteActionError("submit")
                action_obj.execute(identity, uow)
                break
