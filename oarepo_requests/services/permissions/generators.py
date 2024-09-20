from flask_principal import Identity
from invenio_records_permissions.generators import ConditionalGenerator, Generator
from invenio_records_resources.references.entity_resolvers import EntityProxy
from invenio_requests.proxies import current_requests
from invenio_search.engine import dsl
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_workflows.requests.policy import RecipientGeneratorMixin
from sqlalchemy.exc import NoResultFound

from oarepo_requests.services.permissions.identity import request_active


class RequestActive(Generator):

    def needs(self, **kwargs):
        return [request_active]

    def query_filter(self, identity=None, **kwargs):
        return dsl.Q("match_none")


class IfRequestType(ConditionalGenerator):
    def __init__(self, request_types, then_):
        super().__init__(then_, else_=[])
        if not isinstance(request_types, (list, tuple)):
            request_types = [request_types]
        self.request_types = request_types

    def _condition(self, request_type, **kwargs):
        return request_type.type_id in self.request_types


try:
    from oarepo_workflows import WorkflowPermission
    from oarepo_workflows.errors import InvalidWorkflowError, MissingWorkflowError
    from oarepo_workflows.proxies import current_oarepo_workflows

    class CreatorsFromWorkflow(WorkflowPermission):

        def needs(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
                return workflow_request.needs(
                    request_type=request_type, record=record, **kwargs
                )
            except (MissingWorkflowError, InvalidWorkflowError):
                return []

        def excludes(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
                return workflow_request.excludes(
                    request_type=request_type, record=record, **kwargs
                )
            except (MissingWorkflowError, InvalidWorkflowError):
                return []

        # not tested
        def query_filter(self, record=None, request_type=None, **kwargs):
            try:
                workflow_request = current_oarepo_workflows.get_workflow(
                    record
                ).requests()[request_type.type_id]
                return workflow_request.query_filters(
                    request_type=request_type, record=record, **kwargs
                )
            except (MissingWorkflowError, InvalidWorkflowError):
                return dsl.Q("match_none")

except ImportError:
    pass


class IfRequestedBy(RecipientGeneratorMixin, ConditionalGenerator):

    def __init__(self, requesters, then_, else_):
        super().__init__(then_, else_)
        if not isinstance(requesters, (list, tuple)):
            requesters = [requesters]
        self.requesters = requesters

    def _condition(self, *, request_type, creator, **kwargs):
        """Condition to choose generators set."""
        # get needs
        if isinstance(creator, Identity):
            needs = creator.provides
        else:
            if not isinstance(creator, EntityProxy):
                # convert to entityproxy
                creator = current_requests.entity_resolvers_registry.reference_entity(
                    creator
                )
            needs = creator.get_needs()

        for condition in self.requesters:
            condition_needs = set(
                condition.needs(request_type=request_type, creator=creator, **kwargs)
            )
            condition_excludes = set(
                condition.excludes(request_type=request_type, creator=creator, **kwargs)
            )

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
                ret.extend(
                    gen.reference_receivers(
                        record=record, request_type=request_type, **kwargs
                    )
                )
        return ret

    def query_filter(self, **kwargs):
        """Search filters."""
        raise NotImplementedError(
            "Please use IfRequestedBy only in recipients, not elsewhere."
        )


class IfNoNewVersionDraft(ConditionalGenerator):
    def __init__(self, then_, else_=None):
        else_ = [] if else_ is None else else_
        super().__init__(then_, else_=else_)

    def _condition(self, record, **kwargs):
        return not record.is_draft and not record.versions.next_draft_id


class IfNoEditDraft(ConditionalGenerator):
    def __init__(self, then_, else_=None):
        else_ = [] if else_ is None else else_
        super().__init__(then_, else_=else_)

    def _condition(self, record, **kwargs):
        if record.is_draft:
            return False
        records_service = get_record_service_for_record(record)
        try:
            draft = records_service.config.draft_cls.pid.resolve(
                record["id"]
            )  # by edit - has the same id as parent record
            # i'm not sure what open unpublished means
            return False
        except NoResultFound:
            return True
