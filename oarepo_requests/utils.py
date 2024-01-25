from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_search.engine import dsl

from oarepo_requests.errors import OpenRequestAlreadyExists





def get_request_from_record(identity, record, request_type, *args, **kwargs):
    request = getattr(record.parent, request_type, None)
    # request =

    return request


def get_requests_from_record(identity, record, *args, **kwargs):
    try:
        requests = list(
            current_requests_service.scan(
                identity, extra_filter=dsl.Q("query_string", query=record["id"])
            ).hits
        )
    except (
        PermissionDeniedError
    ):  # if user is not allowed to search requests, it should not return any but should still allow reading of the record
        requests = []
    return requests

"""
def get_post_request_url():
    return f"{{+api}}{OARepoRequestsResourceConfig.url_prefix}"
"""


def allowed_request_types_for_record_cls(queryied_record_cls):
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


"""
{'minimum_should_match': '0<1', 
 'filter': [Bool(minimum_should_match=1, 
                 must=[QueryString(query='swf1h-psj10')], 
                 should=[Bool
                         (must=[Terms(status=['created']), 
                                Terms(grants=['created_by.system_role.any_user', 
                                                  'created_by.community.a26e6dfa-86ef-4a3b-9cbb-d6f034533a45.owner', 
                                                  'created_by.id.1', 'created_by.system_role.authenticated_user'])])
                     , 
                         Bool(minimum_should_match=1, must=[Terms(status=['submitted', 'deleted', 'cancelled', 'expired', 'accepted', 'declined'])], 
                        should=[Terms(grants=['created_by.system_role.any_user', 'created_by.community.a26e6dfa-86ef-4a3b-9cbb-d6f034533a45.owner', 'created_by.id.1', 'created_by.system_role.authenticated_user']), Terms(grants=['receiver.system_role.any_user', 'receiver.community.a26e6dfa-86ef-4a3b-9cbb-d6f034533a45.owner', 'receiver.id.1', 'receiver.system_role.authenticated_user'])])])], 'should': []}
"""


def request_exists(
    identity,
    topic,
    type_id,
    topic_type="thesis_draft",
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
        dsl.Q("term", **{"is_open": True}),
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
    existing_request = request_exists(system_identity, topic, type_id)
    if existing_request:
        raise OpenRequestAlreadyExists(existing_request, topic)

# TODO these things are related and possibly could be approached in a less convoluted manner? For example, global model->services map would help
def resolve_reference_dict(reference_dict):
    # from invenio_records_resources.references.registry.ResolverRegistryBase.reference_entity
    topic_resolver = None
    for resolver in ResolverRegistry.get_registered_resolvers():
        try:
            if resolver.matches_reference_dict(reference_dict):
                topic_resolver = resolver
                break
        except ValueError:
            # Value error ignored from matches_reference_dict
            pass
    obj = topic_resolver.proxy_cls(
        topic_resolver, reference_dict, topic_resolver.record_cls
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

