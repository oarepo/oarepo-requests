from invenio_access.permissions import system_identity
from invenio_requests import current_requests_service
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl

from oarepo_requests.errors import OpenRequestAlreadyExists


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


def request_exists(
    identity,
    topic,
    type_id,
    topic_type=None,
    is_open=False,
    receiver_type=None,
    receiver_id=None,
    creator_type=None,
    creator_id=None,
    topic_id=None,
    add_args=None,
):
    """Return the request id if an open request already exists, else None."""

    must = [
        dsl.Q("term", **{"type": type_id}),
        dsl.Q("term", **{"is_open": is_open}),
    ]
    if add_args:
        must += add_args
    if receiver_type:
        must.append(dsl.Q("term", **{f"receiver.{receiver_type}": receiver_id}))
    if creator_type:
        must.append(dsl.Q("term", **{f"creator.{creator_type}": creator_id}))
    if topic_type:
        topic_id = topic_id if topic_id is not None else topic.pid.pid_value
        must.append(dsl.Q("term", **{f"topic.{topic_type}": topic_id}))
    results = current_requests_service.search(
        identity,
        extra_filter=dsl.query.Bool(
            "must",
            must=must,
        ),
    )
    return next(results.hits)["id"] if results.total > 0 else None


def open_request_exists(topic, type_id, creator=None):
    existing_request = request_exists(system_identity, topic, type_id, is_open=True)
    if existing_request:
        raise OpenRequestAlreadyExists(existing_request, topic)


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
    obj = topic_resolver.get_entity_proxy(
        reference_dict
    ).resolve()
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