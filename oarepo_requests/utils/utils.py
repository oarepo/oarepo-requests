from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_requests.proxies import current_request_type_registry

def get_allowed_request_types(queryied_record_cls):
    request_types = current_request_type_registry._registered_types
    resolvers = list(ResolverRegistry.get_registered_resolvers())
    # possibly the mapping doesn't have to be 1:1
    type_key2record_cls = {resolver.type_key:resolver.record_cls for resolver in resolvers if hasattr(resolver, "type_key")}
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