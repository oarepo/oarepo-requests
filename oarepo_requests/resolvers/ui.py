"""UI resolvers of common entities."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, TypedDict, override

from invenio_records_resources.resources.errors import PermissionDeniedError
from invenio_search.engine import dsl
from invenio_users_resources.proxies import (
    current_groups_service,
    current_users_service,
)
from oarepo_runtime.i18n import gettext as _

from ..proxies import current_oarepo_requests
from ..utils import get_matching_service_for_refdict

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.services.records import RecordService as DraftsService
    from invenio_records_resources.services.records.results import RecordItem

    from oarepo_requests.typing import EntityReference


class UIResolvedReference(TypedDict):
    """Resolved UI reference."""

    reference: EntityReference
    type: str
    label: str | LazyString
    links: dict[str, str]


def resolve(identity: Identity, reference: dict[str, str]) -> UIResolvedReference:
    """Resolve a reference to a UI representation.

    :param identity: Identity of the user.
    :param reference: Reference to resolve.
    """
    reference_type, reference_value = next(iter(reference.items()))
    entity_resolvers = current_oarepo_requests.entity_reference_ui_resolvers
    if reference_type in entity_resolvers:
        return entity_resolvers[reference_type].resolve_one(identity, reference_value)
    else:
        # TODO log warning
        return entity_resolvers["fallback"].resolve_one(identity, reference_value)


def fallback_label_result(reference: dict[str, str]) -> str:
    """Get a fallback label for a reference if there is no other way to get it."""
    id_ = list(reference.values())[0]
    return f"id: {id_}"


def fallback_result(reference: dict[str, str]) -> UIResolvedReference:
    """Get a fallback result for a reference if there is no other way to get it."""
    return {
        "reference": reference,
        "type": next(iter(reference.keys())),
        "label": fallback_label_result(reference),
        "links": {},
    }


class OARepoUIResolver(abc.ABC):
    """Base class for entity reference UI resolvers."""

    def __init__(self, reference_type: str) -> None:
        """Initialize the resolver.

        :param reference_type:  type of the reference (the key in the reference dict)
        """
        self.reference_type = reference_type

    @abc.abstractmethod
    def _get_id(self, entity: dict) -> str:
        """Get the id of the serialized entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found. Each entity must be API serialized to dict.
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        :return:            API serialization of the data of the entity or
                            None if the entity no longer exists

        Note: this call must return None if the entity does not exist,
        not raise an exception!
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved and API serialized entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        raise NotImplementedError(f"Implement this in {self.__class__.__name__}")

    def resolve_one(self, identity: Identity, _id: str) -> UIResolvedReference:
        """Resolve a single reference to a UI representation.

        :param identity:    identity of the user
        :param _id:         id of the entity
        :return:            UI representation of the reference
        """
        reference = {self.reference_type: _id}
        entity = self._search_one(identity, _id)
        if not entity:
            return fallback_result(reference)
        resolved = self._get_entity_ui_representation(entity, reference)
        return resolved

    def resolve_many(
        self, identity: Identity, ids: list[str]
    ) -> list[UIResolvedReference]:
        """Resolve many references to UI representations.

        :param identity:    identity of the user
        :param ids:         ids of the records of the type self.reference_type
        :return:            list of UI representations of the references
        """
        search_results = self._search_many(identity, ids)
        ret = []
        result: dict
        for result in search_results:
            # it would be simple if there was a map of results, can opensearch do this?
            ret.append(
                self._get_entity_ui_representation(
                    result, {self.reference_type: self._get_id(result)}
                )
            )
        return ret

    def _extract_links_from_resolved_reference(
        self, resolved_reference: dict
    ) -> dict[str, str]:
        """Extract links from a entity."""
        links = {}
        entity_links = {}
        if "links" in resolved_reference:
            entity_links = resolved_reference["links"]
        for link_type in ("self", "self_html"):
            if link_type in entity_links:
                links[link_type] = entity_links[link_type]
        return links


class GroupEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for group entity references."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        result = []
        for group in ids:
            try:
                group: RecordItem = current_groups_service.read(identity, group)
                result.append(group.data)
            except PermissionDeniedError:
                pass
        return result

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        try:
            group: RecordItem = current_groups_service.read(identity, _id)
            return group.data
        except PermissionDeniedError:
            return None

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        label = entity["name"]
        ret = {
            "reference": reference,
            "type": "group",
            "label": label,
            "links": self._extract_links_from_resolved_reference(entity),
        }
        return ret


class UserEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for user entity references."""

    @override
    def _get_id(self, result: RecordItem) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        result: list[dict] = []
        for user in ids:
            try:
                user: RecordItem = current_users_service.read(identity, user)
                result.append(user.data)
            except PermissionDeniedError:
                pass
        return result

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        try:
            user = current_users_service.read(identity, _id)
            return user.data
        except PermissionDeniedError:
            return None

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if entity["id"] == "system":
            label = _("System user")
        elif (
            "profile" in entity
            and "full_name" in entity["profile"]
            and entity["profile"]["full_name"]
        ):
            label = entity["profile"]["full_name"]
        elif "username" in entity and entity["username"]:
            label = entity["username"]
        else:
            label = fallback_label_result(reference)
        ret = {
            "reference": reference,
            "type": "user",
            "label": label,
            "links": self._extract_links_from_resolved_reference(entity),
        }
        return ret


class RecordEntityReferenceUIResolver(OARepoUIResolver):
    """UI resolver for entity entity references."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not ids:
            return []
        # todo what if search not permitted?
        service = get_matching_service_for_refdict({self.reference_type: list(ids)[0]})
        extra_filter = dsl.Q("terms", **{"id": list(ids)})
        return service.search(identity, extra_filter=extra_filter).data["hits"]["hits"]

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        service = get_matching_service_for_refdict({self.reference_type: _id})
        return service.read(identity, _id).data

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if "metadata" in entity and "title" in entity["metadata"]:
            label = entity["metadata"]["title"]
        else:
            label = fallback_label_result(reference)
        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
            "links": self._extract_links_from_resolved_reference(entity),
        }
        return ret


class RecordEntityDraftReferenceUIResolver(RecordEntityReferenceUIResolver):
    """UI resolver for entity entity draft references."""

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        # using values instead of references breaks the pattern, perhaps it's lesser evil to construct them on go?
        if not ids:
            return []

        service: DraftsService = get_matching_service_for_refdict(
            {self.reference_type: list(ids)[0]}
        )
        extra_filter = dsl.Q("terms", **{"id": list(ids)})
        return service.search_drafts(identity, extra_filter=extra_filter).data["hits"][
            "hits"
        ]

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        service: DraftsService = get_matching_service_for_refdict(
            {self.reference_type: _id}
        )
        return service.read_draft(identity, _id).data


class FallbackEntityReferenceUIResolver(OARepoUIResolver):
    """Fallback UI resolver if no other resolver is found."""

    @override
    def _get_id(self, result: dict) -> str:
        """Get the id of the entity returned from a service.

        :result:    entity returned from a service (as a RecordItem instance)
        """
        return result["id"]

    @override
    def _search_many(
        self, identity: Identity, ids: list[str], *args: Any, **kwargs: Any
    ) -> list[dict]:
        """Search for many records of the same type at once.

        :param identity:    identity of the user
        :param ids:         ids to search for
        :param args:        additional arguments
        :param kwargs:      additional keyword arguments
        :return:            list of records found
        """
        raise NotImplementedError("Intentionally not implemented")

    @override
    def _search_one(
        self, identity: Identity, _id: str, *args: Any, **kwargs: Any
    ) -> dict | None:
        """Search for a single entity of the same type.

        :param identity:    identity of the user
        :param _id:         id to search for
        """
        reference = {self.reference_type: _id}
        try:
            service = get_matching_service_for_refdict(reference)
        except:  # noqa - we don't care which exception has been caught, just returning fallback result
            return fallback_result(reference)

        # TODO: we might have a problem here - draft and published entity can have the same
        # id, but in reference they have the same type. So later on, we can not differentiate
        # between draft and published record.
        # This would be a problem if a single request type could be applicable both to draft
        # and published record.
        try:
            response = service.read(identity, _id)
        except:  # noqa - we don't care which exception has been caught, just returning fallback result
            try:
                response = service.read_draft(identity, _id)  # type: ignore
            except:  # noqa - we don't care which exception has been caught, just returning fallback result
                return fallback_result(reference)

        if hasattr(response, "data"):
            response = response.data
        return response

    @override
    def _get_entity_ui_representation(
        self, entity: dict, reference: EntityReference
    ) -> UIResolvedReference:
        """Create a UI representation of a entity.

        :entity:        resolved entity
        :reference:     reference to the entity
        :return:        UI representation of the entity
        """
        if "metadata" in entity and "title" in entity["metadata"]:
            label = entity["metadata"]["title"]
        else:
            label = fallback_label_result(reference)

        ret = {
            "reference": reference,
            "type": list(reference.keys())[0],
            "label": label,
            "links": self._extract_links_from_resolved_reference(entity),
        }
        return ret
