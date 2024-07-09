from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl
from oarepo_workflows.permissions.generators import needs_from_generators

from oarepo_requests.utils import get_from_requests_workflow

from .identity import autoapprove, autorequest, request_active


class CreatorsFromWorkflow(Generator):
    def _get_workflow_id(self, request_type, *args, **kwargs):
        if "record" in kwargs:
            return kwargs["record"].parent["workflow"]
        return "default"

    def needs(self, request_type, *args, **kwargs):
        # todo load from community
        workflow_id = self._get_workflow_id(request_type, *args, **kwargs)
        try:
            creators_generators = get_from_requests_workflow(
                workflow_id, request_type.type_id, "requesters"
            )
        except KeyError:
            return []
        needs = needs_from_generators(
            creators_generators, *args, request_type=request_type, **kwargs
        )
        return needs


class AutoRequest(Generator):
    def needs(self, **kwargs):
        return [autorequest]


class AutoApprove(Generator):
    def needs(self, **kwargs):
        return [autoapprove]


class RequestActive(Generator):

    def needs(self, **kwargs):
        return [request_active]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as system process."""
        if request_active in identity.provides:
            return dsl.Q("match_all")
        else:
            return []
