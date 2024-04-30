from invenio_records_resources.resources.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)

from ..proxies import current_oarepo_requests
from ..utils import get_matching_service_for_refdict


def resolve(identity, reference):
    reference_type = list(reference.keys())[0]
    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers
    if reference_type in entity_resolvers:
        return entity_resolvers[reference_type].resolve_one(identity, reference)
    else:
        # TODO log warning
        return entity_resolvers["fallback"].resolve_one(identity, reference)


def fallback_label_result(reference):
    id_ = list(reference.values())[0]
    return f"id: {id_}"


def fallback_result(reference):
    type = list(reference.keys())[0]
    return {
        "reference": reference,
        "type": type,
        "label": fallback_label_result(reference),
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

    def _resolve(self, record, reference):
        raise NotImplementedError("Parent entity ui resolver should be abstract")

    def resolve_one(self, identity, reference):
        # todo - control if reference aligns with reference_type
        # reference is on input for copying the invenio pattern (?)
        record = self._search_one(identity, reference)
        if not record:
            return fallback_result(reference)
        resolved = self._resolve(record, reference)
        return resolved

    def resolve_many(self, identity, values):
        # the pattern is broken here by using values instead of reference?
        search_results = self._search_many(identity, values)
        ret = []
        for result in search_results:
            # it would be simple if there was a map of results, can opensearch do this?
            ret.append(
                self._resolve(result, {self.reference_type: self._get_id(result)})
            )
        return ret


class GroupEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        return result.data["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        result = []
        for user in values:
            try:
                user = current_groups_service.read(identity, user)
                result.append(user)
            except PermissionDeniedError:
                pass
        return result

    def _search_one(self, identity, reference, *args, **kwargs):
        value = list(reference.values())[0]
        try:
            user = current_groups_service.read(identity, value)
            return user
        except PermissionDeniedError:
            return None

    def _resolve(self, record, reference):
        # todo; this is copyied from user
        if record.data["username"] is None:  # username undefined?
            if "email" in record.data:
                label = record.data["email"]
            else:
                label = fallback_label_result(reference)
        else:
            label = record.data["username"]
        ret = {
            "reference": reference,
            "type": "user",
            "label": label,
        }
        if "links" in record.data and "self" in record.data["links"]:
            ret["link"] = record.data["links"]["self"]
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

    def _resolve(self, record, reference):
        if record.data["username"] is None:  # username undefined?
            if "email" in record.data:
                label = record.data["email"]
            else:
                label = fallback_label_result(reference)
        else:
            label = record.data["username"]
        ret = {
            "reference": reference,
            "type": "user",
            "label": label,
        }
        if "links" in record.data and "self" in record.data["links"]:
            ret["link"] = record.data["links"]["self"]
        return ret


class RecordEntityReferenceUIResolver(OARepoUIResolver):
    def _get_id(self, result):
        return result["id"]

    def _search_many(self, identity, values, *args, **kwargs):
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not values:
            return []
        service = get_matching_service_for_refdict(
            {self.reference_type: list(values)[0]}
        )
        filter = dsl.Q("terms", **{"id": list(values)})
        return list(service.search(identity, extra_filter=filter).hits)

    def _search_one(self, identity, reference, *args, **kwargs):
        id = list(reference.values())[0]
        service = get_matching_service_for_refdict(reference)
        return service.read(identity, id).data

    def _resolve(self, record, reference):
        if "metadata" in record and "title" in record["metadata"]:
            label = record["metadata"]["title"]
        else:
            label = fallback_label_result(reference)
        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
            "link": record["links"]["self"],
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
        # todo extra filter doesn't work in rdm-11
        filter = dsl.Q("terms", **{"id": list(values)})
        try:
            ret = list(service.search_drafts(identity, extra_filter=filter).hits)
        except TypeError:
            # ----
            from invenio_records_resources.services.base.links import LinksTemplate

            # rdm-12 version
            def search_drafts(
                service,
                identity,
                params=None,
                search_preference=None,
                expand=False,
                extra_filter=None,
                **kwargs,
            ):
                """Search for drafts records matching the querystring."""
                service.require_permission(identity, "search_drafts")

                # Prepare and execute the search
                params = params or {}

                search_draft_filter = dsl.Q("term", has_draft=False)

                if extra_filter:
                    search_draft_filter &= extra_filter

                search_result = service._search(
                    "search_drafts",
                    identity,
                    params,
                    search_preference,
                    record_cls=service.draft_cls,
                    search_opts=service.config.search_drafts,
                    # `has_draft` systemfield is not defined here. This is not ideal
                    # but it helps avoid overriding the method. See how is used in
                    # https://github.com/inveniosoftware/invenio-rdm-records
                    extra_filter=dsl.Q("term", has_draft=False),
                    permission_action="read_draft",
                    **kwargs,
                ).execute()

                return service.result_list(
                    service,
                    identity,
                    search_result,
                    params,
                    links_tpl=LinksTemplate(
                        service.config.links_search_drafts, context={"args": params}
                    ),
                    links_item_tpl=service.links_item_tpl,
                    expandable_fields=service.expandable_fields,
                    expand=expand,
                )

            ret = list(search_drafts(service, identity, extra_filter=filter).hits)

            # ----
        return ret

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

    def _resolve(self, record, reference):
        if "metadata" in record and "title" in record["metadata"]:
            label = record["metadata"]["title"]
        else:
            label = fallback_label_result(reference)

        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
        }
        if "links" in record and "self" in record["links"]:
            ret["link"] = record["links"]["self"]
        return ret
