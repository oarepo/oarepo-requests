from collections import defaultdict

from flask import g
from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from ..services.ui_schema import UIBaseRequestSchema
from ..utils import get_matching_service_for_refdict


def groups_search(identity, reference_type, values, *args, **kwargs):
    result = []
    for user in values:
        try:
            user = current_groups_service.read(identity, user)
            result.append(user)
        except PermissionDeniedError:
            pass
    return result


def users_search(identity, reference_type, values, *args, **kwargs):
    result = []
    for user in values:
        try:
            user = current_users_service.read(identity, user)
            result.append(user)
        except PermissionDeniedError:
            pass
    return result


def drafts_search(identity, reference_type, values, *args, **kwargs):
    service = get_matching_service_for_refdict({reference_type: list(values)[0]})
    # service.draft_cls.index.refresh()
    filter = dsl.Q("terms", **{"id": list(values)})
    return list(service.search_drafts(identity, extra_filter=filter).hits)


def records_search(identity, reference_type, values, *args, **kwargs):
    service = get_matching_service_for_refdict({reference_type: list(values)[0]})
    # service.record_cls.index.refresh()
    filter = dsl.Q("terms", **{"id": list(values)})
    return list(service.search(identity, extra_filter=filter).hits)


BULK_SEARCHES = {
    "user": users_search,
    # "group": groups_search,
    "documents_draft": drafts_search,
    "documents": records_search,
    "thesis_draft": drafts_search,
    "thesis": records_search,
}

REFERENCE_TYPES = {"created_by", "receiver", "topic"}


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

    def _reference_map_from_object(self, obj):
        reference_map = defaultdict(set)
        for reference_type in REFERENCE_TYPES:
            if reference_type in obj:
                reference = obj[reference_type]
                reference_map[list(reference.keys())[0]].add(
                    list(reference.values())[0]
                )
        return reference_map

    def _reference_map_from_list(self, obj_list):
        hits = obj_list["hits"]["hits"]
        reference_map = defaultdict(set)
        for hit in hits:
            for reference_type in REFERENCE_TYPES:
                if reference_type in hit:
                    reference = hit[reference_type]
                    reference_map[list(reference.keys())[0]].add(
                        list(reference.values())[0]
                    )
        return reference_map

    def _get_resolved_map(self, reference_map, ctx):
        resolved_map = {}
        for reference_type, values in reference_map.items():
            if reference_type in BULK_SEARCHES:
                search_method = BULK_SEARCHES[reference_type]
                result = search_method(ctx["identity"], reference_type, values)
                resolved_map[reference_type] = result
        return resolved_map

    def dump_obj(self, obj, *args, **kwargs):
        extra_context = {
            "resolved": self._get_resolved_map(
                self._reference_map_from_object(obj), self.schema_context
            )
        }
        return super().dump_obj(obj, *args, extra_context=extra_context, **kwargs)

    def dump_list(self, obj_list, *args, **kwargs):
        extra_context = {
            "resolved": self._get_resolved_map(
                self._reference_map_from_list(obj_list), self.schema_context
            )
        }
        return super().dump_list(obj_list, *args, extra_context=extra_context, **kwargs)
