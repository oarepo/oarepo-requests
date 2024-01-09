"""
import copy
from collections import defaultdict

from invenio_records_resources.services.base.links import Link
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.proxies import current_requests_service


def is_action_available(request, context):
    identity = context.get("identity")
    action = context.get("action")
    permission = current_requests_service.config.permission_policy_cls(
        f"action_{action}", request=request
    )
    return RequestActions.can_execute(request, action) and permission.allows(identity)


class RecordRequestsLink(Link):

    def expand(self, request, context):
        request_links = defaultdict(str)
        for action in request.type.available_actions:
            if action in [request.type.create_action, request.type.delete_action]:
                continue
            ctx = copy.deepcopy(context)
            self.vars = lambda record, vars: vars.update(
                {"id": str(request.id), "action": action}
            )
            if is_action_available(action, request, ctx):
                request_links[action] = super().expand(request, ctx)
        return request_links
"""
