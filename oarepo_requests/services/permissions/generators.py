from invenio_records_permissions.generators import Generator, ConditionalGenerator
from invenio_search.engine import dsl

from oarepo_requests.services.permissions.identity import request_active
from oarepo_workflows.requests.policy import RecipientGeneratorMixin
from flask_principal import Identity

from invenio_requests.proxies import current_requests
from invenio_records_resources.references.entity_resolvers import EntityProxy


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


class IfRequestedBy(RecipientGeneratorMixin, ConditionalGenerator):

    def __init__(self, conditions, then_, else_):
        super().__init__(then_, else_)
        if not isinstance(conditions, (list, tuple)):
            conditions = [conditions]
        self._conditions = conditions

    def _condition(self, *, request_type, creator, **kwargs):
        """Condition to choose generators set."""
        # get needs
        if isinstance(creator, Identity):
            needs = creator.provides
        else:
            if not isinstance(creator, EntityProxy):
                # convert to entityproxy
                creator = current_requests.entity_resolvers_registry.reference_entity(creator)
            needs = creator.get_needs()

        for condition in self._conditions:
            condition_needs = set(condition.needs(request_type=request_type, creator=creator, **kwargs))
            condition_excludes = set(condition.excludes(request_type=request_type, creator=creator, **kwargs))

            if not condition_needs.intersection(needs):
                continue
            if condition_excludes and condition_excludes.intersection(needs):
                continue
            return True
        return False

    def reference_receivers(self, record=None, request_type=None, **kwargs):
        ret = []
        for gen in self._generators(record=record, request_type=request_type, **kwargs):
            if isinstance(gen, RecipientGeneratorMixin):
                ret.extend(gen.reference_receivers(record=record, request_type=request_type, **kwargs))
        return ret

    def query_filter(self, **kwargs):
        """Search filters."""
        raise NotImplementedError("Please use IfRequestedBy only in recipients, not elsewhere.")
