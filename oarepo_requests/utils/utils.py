from copy import deepcopy

from invenio_requests.proxies import current_request_type_registry
from invenio_requests.resolvers.registry import ResolverRegistry
from collections import defaultdict


def get_allowed_request_types(queryied_record_cls):
    request_types = current_request_type_registry._registered_types
    resolvers = list(ResolverRegistry.get_registered_resolvers())
    # possibly the mapping doesn't have to be 1:1
    type_key2record_cls = {
        resolver.type_key: resolver.record_cls
        for resolver in resolvers
        if hasattr(resolver, "type_key")
    }
    ret = {}
    for request_name, request_type in request_types.items():
        allowed_type_keys = set(request_type.allowed_topic_ref_types)
        for allowed_type_key in allowed_type_keys:
            if allowed_type_key not in type_key2record_cls:
                continue
            record_cls = type_key2record_cls[allowed_type_key]
            if record_cls == queryied_record_cls:
                ret[request_name] = request_type
                break
    return ret

from invenio_requests.customizations.actions import RequestActions
from invenio_requests.proxies import current_requests
def is_action_available(action, request, context):
    """Check if the given action is available on the request."""
    identity = context.get("identity")
    permission = current_requests.requests_service.config.permission_policy_cls(f"action_{action}", request=request)
    return RequestActions.can_execute(request, action) and permission.allows(identity)



from invenio_records_resources.services.base.links import Link, LinksTemplate


def expand(self, identity, obj):
    """Expand all the link templates."""
    links = {}
    ctx = deepcopy(self.context)
    # pass identity to context
    ctx["identity"] = identity
    for key, link in self._links.items():
        if link.should_render(obj, ctx):
            links[key] = link.expand(obj, ctx)
    return links

class RecordRequestsLinksTemplate(LinksTemplate):

    def __init__(self, links, action_link, request_types, context=None):

        super().__init__(links, context=context)
        self._action_link = action_link
        self._request_types = request_types

    def expand(self, identity, obj):
        request_links = defaultdict(dict)
        links = {}
        # expand links for all available actions on the request
        link = self._action_link
        for request_type in self._request_types:
            request = getattr(obj.parent, request_type, None)
            if request is None:
                continue
            req = request.get_object()
            for action in req.type.available_actions:
                if action in [req.type.create_action, req.type.delete_action]:
                    continue
                ctx = self.context.copy()
                ctx["action"] = action
                ctx["identity"] = identity
                ctx["permission_policy_cls"] = current_requests.requests_service.config.permission_policy_cls
                if link.should_render(req, ctx):
                    request_links[request_type][action] = link.expand(req, ctx)

        ctx = deepcopy(self.context)
        # pass identity to context
        ctx["identity"] = identity
        for key, link in self._links.items():
            if link.should_render(obj, ctx):
                links[key] = link.expand(obj, ctx)

        return links | request_links

