from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.resources.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from oarepo_runtime.i18n import gettext as _

from ..proxies import current_oarepo_requests
from ..utils import get_matching_service_for_refdict


def resolve(identity, reference, **kwargs):
    reference_type = list(reference.keys())[0]
    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers
    if reference_type in entity_resolvers:
        return entity_resolvers[reference_type].resolve_one(
            identity, reference, **kwargs
        )
    else:
        # TODO log warning
        return entity_resolvers["fallback"].resolve_one(identity, reference, **kwargs)


def fallback_label_result(reference, **kwargs):
    id_ = list(reference.values())[0]
    return f"id: {id_}"


def fallback_result(reference, **kwargs):
    type = list(reference.keys())[0]
    return {
        "reference": reference,
        "type": type,
        "label": fallback_label_result(reference, **kwargs),
    }


class OARepoUIResolver:
    def __init__(self, reference_type):
        self.reference_type = reference_type

    def _get_id(self, result):
        raise NotImplementedError("Parent entity ui resolver should be abstract")

    def _search_many(self, identity, values, *args, **kwargs):
        raise NotImplementedError("Parent entity ui resolver should be abstract")

    def _search_one(self, identity, reference, *args, **kwargs):
        raise NotImplementedError("Parent entity ui resolver should be abstract")

    def _resolve(self, record, reference, **kwargs):
        raise NotImplementedError("Parent entity ui resolver should be abstract")

    def resolve_one(self, identity, reference, **kwargs):
        try:
            record = self._search_one(identity, reference)
            if not record:
                return fallback_result(reference, **kwargs)
        except PIDDoesNotExistError:
            return fallback_result(reference, **kwargs)
        resolved = self._resolve(record, reference, **kwargs)
        return resolved

    def resolve_many(self, identity, values, **kwargs):
        # the pattern is broken here by using values instead of reference?
        search_results = self._search_many(identity, values)
        ret = []
        for result in search_results:
            # it would be simple if there was a map of results, can opensearch do this?
            ret.append(
                self._resolve(result, {self.reference_type: self._get_id(result)})
            )
        return ret

    def _resolve_links(self, record, keep_all_links=False, **kwargs):
        links = {}
        record_links = {}
        if isinstance(record, dict):
            if "links" in record:
                record_links = record["links"]
        elif hasattr(record, "data"):
            if "links" in record.data:
                record_links = record.data["links"]
        if keep_all_links:
            return record_links
        for link_type in ("self", "self_html"):
            if link_type in record_links:
                links[link_type] = record_links[link_type]
        return links


class GroupEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        return result.data["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        result = []
        for group in values:
            try:
                group = current_groups_service.read(identity, group)
                result.append(group)
            except PermissionDeniedError:
                pass
        return result

    def _search_one(self, identity, reference, *args, **kwargs):
        value = list(reference.values())[0]
        try:
            group = current_groups_service.read(identity, value)
            return group
        except PermissionDeniedError:
            return None

    def _resolve(self, record, reference, **kwargs):
        label = record.data["name"]
        ret = {
            "reference": reference,
            "type": "group",
            "label": label,
            "links": self._resolve_links(record, **kwargs),
        }
        return ret


class UserEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        return result.data["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        result = []
        for user in values:
            try:
                user = current_users_service.read(identity, user)
                result.append(user)
            except PermissionDeniedError:
                pass
        return result

    def _search_one(self, identity, reference, *args, **kwargs):
        value = list(reference.values())[0]
        try:
            user = current_users_service.read(identity, value)
            return user
        except PermissionDeniedError:
            return None

    def _resolve(self, record, reference, **kwargs):

        if record.data["id"] == "system":
            label = _("System user")
        elif (
            "profile" in record.data
            and "full_name" in record.data["profile"]
            and record.data["profile"]["full_name"]
        ):
            label = record.data["profile"]["full_name"]
        elif "username" in record.data and record.data["username"]:
            label = record.data["username"]
        else:
            label = fallback_label_result(reference, **kwargs)
        ret = {
            "reference": reference,
            "type": "user",
            "label": label,
            "links": self._resolve_links(record, **kwargs),
        }
        return ret


class RecordEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        return result["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not values:
            return []
        # todo what if search not permitted?
        service = get_matching_service_for_refdict(
            {self.reference_type: list(values)[0]}
        )
        filter = dsl.Q("terms", **{"id": list(values)})
        return list(service.search(identity, extra_filter=filter).hits)

    def _search_one(self, identity, reference, *args, **kwargs):
        id = list(reference.values())[0]
        service = get_matching_service_for_refdict(reference)
        return service.read(identity, id).data

    def _resolve(self, record, reference, **kwargs):
        if "metadata" in record and "title" in record["metadata"]:
            label = record["metadata"]["title"]
        else:
            label = fallback_label_result(reference, **kwargs)
        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
            "links": self._resolve_links(record, **kwargs),
        }
        return ret


class RecordEntityDraftReferenceUIResolver(RecordEntityReferenceUIResolver):
    def _search_many(self, identity, values, *args, **kwargs):
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not values:
            return []

        service = get_matching_service_for_refdict(
            {self.reference_type: list(values)[0]}
        )
        filter = dsl.Q("terms", **{"id": list(values)})
        return list(service.search_drafts(identity, extra_filter=filter).hits)

    def _search_one(self, identity, reference, *args, **kwargs):
        id = list(reference.values())[0]
        service = get_matching_service_for_refdict(reference)
        return service.read_draft(identity, id).data


class FallbackEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        if hasattr(result, "data"):
            return result.data["id"]
        return result["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        """"""

    def _search_one(self, identity, reference, *args, **kwargs):
        id = list(reference.values())[0]
        try:
            service = get_matching_service_for_refdict(reference)
        except:
            return fallback_result(reference)
        try:
            response = service.read(identity, id)
        except:
            try:
                response = service.read_draft(identity, id)
            except:
                return fallback_result(reference)
        if hasattr(response, "data"):
            response = response.data
        return response

    def _resolve(self, record, reference, **kwargs):
        if "metadata" in record and "title" in record["metadata"]:
            label = record["metadata"]["title"]
        else:
            label = fallback_label_result(reference, **kwargs)

        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
            "links": self._resolve_links(record, **kwargs),
        }
        return ret
