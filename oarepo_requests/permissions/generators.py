
from invenio_access.permissions import system_identity
from invenio_records_permissions.generators import Generator
from invenio_requests import current_request_type_registry
from invenio_search.engine import dsl
from oarepo_workflows import WorkflowPermission
from oarepo_workflows.proxies import current_oarepo_workflows

from oarepo_requests.errors import UnknownRequestType
from oarepo_requests.permissions.identity import request_active
from oarepo_requests.utils import (
    get_matching_service_for_record,
    get_requests_service_for_records_service,
)


class RequestActive(Generator):

    def needs(self, **kwargs):
        return [request_active]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as system process."""
        if request_active in identity.provides:
            return dsl.Q("match_all")
        else:
            return []


class CreatorsFromWorkflow(WorkflowPermission):
    """

    def _get_permissions_from_workflow(self, record=None, request_type=None, **kwargs):
        workflow_id = self._get_workflow_id(record, **kwargs)
        needs = current_oarepo_workflows.get_workflow(workflow_id).requesters_needs(request_type=request_type,
                                                                                    record=record, **kwargs)

        if workflow_id not in current_oarepo_workflows.record_workflows:
            raise InvalidWorkflowError(
                f"Workflow {workflow_id} does not exist in the configuration."
            )
        policy_cls = current_oarepo_workflows.record_workflows[workflow_id].requests_cls
        return policy_cls(workflow_field="requesters", record=record, **kwargs)
    """

    def needs(self, record=None, request_type=None, **kwargs):
        workflow_id = self._get_workflow_id(record, **kwargs)
        needs = current_oarepo_workflows.get_workflow(workflow_id).requesters_needs(
            request_type=request_type, record=record, **kwargs
        )
        return needs

    #not tested
    def query_filter(self, record=None, request_type=None, **kwargs):
        workflow_id = self._get_workflow_id(record, **kwargs)
        return current_oarepo_workflows.get_workflow(workflow_id).requests_obj(
            request_type=request_type, workflow_field="requesters", **kwargs
        ).query_filters



class RecordRequestsReceivers(Generator):
    def needs(self, record=None, **kwargs):
        service = get_requests_service_for_records_service(
            get_matching_service_for_record(record)
        )
        reader = (
            service.search_requests_for_draft
            if getattr(record, "is_draft", False)
            else service.search_requests_for_record
        )
        requests = list(reader(system_identity, record["id"]).hits)
        needs = set()
        for request in requests:
            request_type = request["type"]
            type_ = current_request_type_registry.lookup(request_type, quiet=True)
            if not type_:
                raise UnknownRequestType(request_type)
            workflow_id = current_oarepo_workflows.get_workflow_from_record(record)
            request_needs = current_oarepo_workflows.get_workflow(
                workflow_id
            ).recipients_needs(request_type=type_, record=record, **kwargs)
            needs |= request_needs
        return needs

        """
        request_type = kwargs["request_type"]
        workflow_id = current_oarepo_workflows.get_workflow_from_record(record)

        generators = get_from_requests_workflow(
            workflow_id, request_type.type_id, "recipients"
        )

        needs = [
            g.needs(
                record=record,
                **kwargs,
            )
            for g in generators
        ]
        return set(chain.from_iterable(needs))
        """

        # from rdm
        """
        if record is None or record.parent.review is None:
            return []

        # we only expect submission review requests here
        # and as such, we expect the receiver to be a community
        # and the topic to be a record
        request = record.parent.review
        receiver = request.receiver
        if receiver is not None:
            return receiver.get_needs(ctx=request.type.needs_context)
        return []
        """

        """
        the search method checks this in can_read -> infinite recursion; must be done differently
        service = get_requests_service_for_records_service(
            get_matching_service_for_record(record)
        )
        reader = (
            service.search_requests_for_draft
            if getattr(record, "is_draft", False)
            else service.search_requests_for_record
        )

        requests = list(reader(system_identity, record["id"]).hits)

        needs = []
        for request in requests:
            needs += request.receiver.get_needs(ctx=request.type.needs_context)
        return needs
        """
