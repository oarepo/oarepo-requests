from invenio_access.permissions import system_identity
from invenio_requests import current_requests_service
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl


def allowed_request_types_for_record(record):
    request_types = current_request_type_registry._registered_types
    ret = {}
    try:
        record_ref = list(ResolverRegistry.reference_entity(record).keys())[0]
    except:
        # log?
        return ret
    for request_name, request_type in request_types.items():
        allowed_type_keys = set(request_type.allowed_topic_ref_types)
        if record_ref in allowed_type_keys:
            ret[request_name] = request_type
    return ret


def allowed_request_types_for_record_cls(queryied_record_cls):
    # works only for record resolvers which have record_cls and type_key
    # and assumes 1:1 type_key - record_cls mapping; type key is the serialized type name in the ref dict

    request_types = current_request_type_registry._registered_types
    resolvers = list(ResolverRegistry.get_registered_resolvers())
    # possibly the mapping doesn't have to be 1:1
    type_key2record_cls = {
        resolver.type_key: resolver.record_cls
        for resolver in resolvers
        if hasattr(resolver, "type_key") and hasattr(resolver, "record_cls")
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


def _reference_query_term(term, reference):
    return dsl.Q(
        "term", **{f"{term}.{list(reference.keys())[0]}": list(reference.values())[0]}
    )


def search_requests(
    identity,
    type_id,
    topic_reference=None,
    receiver_reference=None,
    creator_reference=None,
    is_open=False,
    add_args=None,
):
    """Return the request id if an open request already exists, else None."""

    must = [
        dsl.Q("term", **{"type": type_id}),
        dsl.Q("term", **{"is_open": is_open}),
    ]
    if receiver_reference:
        must.append(_reference_query_term("receiver", receiver_reference))
    if creator_reference:
        must.append(_reference_query_term("creator", creator_reference))
    if topic_reference:
        must.append(_reference_query_term("topic", topic_reference))
    if add_args:
        must += add_args
    results = current_requests_service.search(
        identity,
        extra_filter=dsl.query.Bool(
            "must",
            must=must,
        ),
    )
    return results.hits


def open_request_exists(topic_or_reference, type_id):
    topic_reference = ResolverRegistry.reference_entity(topic_or_reference, raise_=True)
    existing_requests = search_requests(
        system_identity, type_id, topic_reference=topic_reference, is_open=True
    )
    return bool(list(existing_requests))


# TODO these things are related and possibly could be approached in a less convoluted manner? For example, global model->services map would help
def resolve_reference_dict(reference_dict):
    topic_resolver = None
    for resolver in ResolverRegistry.get_registered_resolvers():
        try:
            if resolver.matches_reference_dict(reference_dict):
                topic_resolver = resolver
                break
        except ValueError:
            # Value error ignored from matches_reference_dict
            pass
    obj = topic_resolver.get_entity_proxy(reference_dict).resolve()
    return obj


def get_matching_service_for_refdict(reference_dict):
    for resolver in ResolverRegistry.get_registered_resolvers():
        if resolver.matches_reference_dict(reference_dict):
            return current_service_registry.get(resolver._service_id)
    return None


def get_matching_service_for_record(record):
    for resolver in ResolverRegistry.get_registered_resolvers():
        if resolver.matches_entity(record):
            return current_service_registry.get(resolver._service_id)
    return None


def get_type_id_for_record_cls(record_cls):
    for resolver in ResolverRegistry.get_registered_resolvers():
        if hasattr(resolver, "record_cls") and resolver.record_cls == record_cls:
            return resolver.type_id
    return None


from invenio_records_resources.proxies import current_service_registry


def get_requests_service_for_records_service(records_service):
    return current_service_registry.get(f"{records_service.config.service_id}_requests")


def stringify_first_val(dct):
    if isinstance(dct, dict):
        for k, v in dct.items():
            dct[k] = str(v)
    return dct


def is_record(record, ctx):
    """Shortcut for links to determine if record is a record."""
    if not hasattr(record, "is_draft"):
        return True
    return not record.is_draft
