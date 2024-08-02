from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl

from oarepo_requests.services.permissions.identity import request_active


class RequestActive(Generator):

    def needs(self, **kwargs):
        return [request_active]

    def query_filter(self, identity=None, **kwargs):
        return dsl.Q("match_none")


try:
    from oarepo_workflows import WorkflowPermission
    from oarepo_workflows.proxies import current_oarepo_workflows

    class CreatorsFromWorkflow(WorkflowPermission):

        def needs(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
            except KeyError:
                return []
            return workflow_request.needs(
                request_type=request_type, record=record, **kwargs
            )

        def excludes(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
            except KeyError:
                return []
            return workflow_request.excludes(
                request_type=request_type, record=record, **kwargs
            )

        # not tested
        def query_filter(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
            except KeyError:
                return dsl.Q("match_none")
            return workflow_request.query_filters(
                request_type=request_type, record=record, **kwargs
            )

except ImportError:
    pass


"""
#if needed, have to implement filter
class RecordRequestsReceivers(Generator):
    def needs(self, record=None, **kwargs):
        service = get_requests_service_for_records_service(
            get_record_service_for_record(record)
        )
        reader = (
            service.search_requests_for_draft
            if getattr(record, "is_draft", False)
            else service.search_requests_for_record
        )
        requests = list(reader(system_identity, record["id"]).hits)
        needs = set()
        for request in requests:
            request_type_id = request["type"]
            type_ = current_request_type_registry.lookup(request_type_id, quiet=True)
            if not type_:
                raise UnknownRequestType(request_type_id)
            workflow_request = current_oarepo_workflows.get_workflow(record).requests()[
                request_type_id
            ]
            request_needs = {
                need
                for generator in workflow_request.recipients
                for need in generator.needs(**kwargs)
            }
            needs |= request_needs
        return needs
"""
