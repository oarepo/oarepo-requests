from invenio_access.permissions import system_identity
from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl
from oarepo_workflows import WorkflowPermission
from oarepo_workflows.utils import get_workflow_from_record

from oarepo_requests.permissions.identity import request_active
from oarepo_requests.utils import get_from_requests_workflow


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
    generator for accesing request creators
    """

    def _get_generators(self, record, **kwargs):
        request_type = kwargs["request_type"]
        workflow_id = get_workflow_from_record(record)
        return get_from_requests_workflow(
            workflow_id, request_type.type_id, "requesters"
        )




class RecordRequestsReceivers(Generator):
    # todo - discussion of how this should actually work

    def needs(self, record=None, **kwargs):
        """
        # from rdm

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
        return []
