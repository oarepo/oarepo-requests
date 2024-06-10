from collections import defaultdict

from flask import g
from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from invenio_pidstore.errors import PIDDeletedError
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from ..proxies import current_oarepo_requests
from ..resolvers.ui import resolve
from ..services.ui_schema import UIBaseRequestSchema
from ..utils import reference_to_tuple


def _reference_map_from_list(obj_list):
    if not obj_list:
        return {}
    hits = obj_list["hits"]["hits"]
    reference_map = defaultdict(set)
    reference_types = current_oarepo_requests.ui_serialization_referenced_fields
    for hit in hits:
        for reference_type in reference_types:
            if reference_type in hit:
                reference = hit[reference_type]
                reference_map[list(reference.keys())[0]].add(
                    list(reference.values())[0]
                )
    return reference_map


def _create_cache(identity, reference_map):
    cache = {}
    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers
    for reference_type, values in reference_map.items():
        if reference_type in entity_resolvers:
            resolver = entity_resolvers[reference_type]
            results = resolver.resolve_many(identity, values)
            # we are expecting "reference" in results
            cache_for_type = {
                reference_to_tuple(result["reference"]): result for result in results
            }
            cache |= cache_for_type
    return cache


class CachedReferenceResolver:
    def __init__(self, identity, references):
        reference_map = _reference_map_from_list(references)
        self._cache = _create_cache(identity, reference_map)
        self._identity = identity

    def dereference(self, reference, **kwargs):
        key = reference_to_tuple(reference)
        if key in self._cache:
            return self._cache[key]
        else:
            try:
                return resolve(self._identity, reference)
            except PIDDeletedError:
                return {"reference": reference, "status": "deleted"}


class OARepoRequestsUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIBaseRequestSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )

    def dump_obj(self, obj, *args, **kwargs):
        # do not create; there's no benefit for caching single objects now
        extra_context = {
            "resolved": CachedReferenceResolver(self.schema_context["identity"], [])
        }
        return super().dump_obj(obj, *args, extra_context=extra_context, **kwargs)

    def dump_list(self, obj_list, *args, **kwargs):
        extra_context = {
            "resolved": CachedReferenceResolver(
                self.schema_context["identity"], obj_list
            )
        }
        return super().dump_list(obj_list, *args, extra_context=extra_context, **kwargs)
