"""Base request type for OARepo requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.customizations import RequestType
from invenio_requests.customizations.states import RequestState
from invenio_requests.proxies import current_requests_service

from oarepo_requests.errors import OpenRequestAlreadyExists
from oarepo_requests.utils import open_request_exists

from ..actions.generic import (
    OARepoAcceptAction,
    OARepoCancelAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from .ref_types import ModelRefTypes, ReceiverRefTypes

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request

    from oarepo_requests.typing import EntityReference


class OARepoRequestType(RequestType):
    """Base request type for OARepo requests."""

    description = None

    dangerous = False

    def on_topic_delete(self, request: Request, topic: Record) -> None:
        """Cancel the request when the topic is deleted.

        :param request:         the request
        :param topic:           the topic
        """
        current_requests_service.execute_action(system_identity, request.id, "cancel")

    @classmethod
    @property
    def available_statuses(cls) -> dict[str, RequestState]:
        """Return available statuses for the request type.

        The status (open, closed, undefined) are used for request filtering.
        """
        return {**super().available_statuses, "created": RequestState.OPEN}

    @classmethod
    @property
    def has_form(cls) -> bool:
        """Return whether the request type has a form."""
        return hasattr(cls, "form")

    @classmethod
    @property
    def editable(cls) -> bool:
        """Return whether the request type is editable."""
        return cls.has_form  # noqa

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: EntityReference,
        topic: Record,
        creator: EntityReference,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created.

        :param identity:        identity of the caller
        :param data:            data of the request
        :param receiver:        receiver of the request
        :param topic:           topic of the request
        :param creator:         creator of the request
        :param args:            additional arguments
        :param kwargs:          additional keyword arguments
        """
        current_requests_service.require_permission(
            identity, "create", record=topic, request_type=self, **kwargs
        )

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic.

        Used for checking whether there is any situation where the client can create
        a request of this type it's different to just using can create with no receiver
        and data because that checks specifically for situation without them while this
        method is used to check whether there is a possible situation a user might create
        this request eg. for the purpose of serializing a link on associated record
        """
        try:
            current_requests_service.require_permission(
                identity, "create", record=topic, request_type=cls, **kwargs
            )
        except PermissionDeniedError:
            return False
        return True

    allowed_topic_ref_types = ModelRefTypes()
    allowed_receiver_ref_types = ReceiverRefTypes()

    @classmethod
    @property
    def available_actions(cls) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": OARepoSubmitAction,
            "accept": OARepoAcceptAction,
            "decline": OARepoDeclineAction,
            "cancel": OARepoCancelAction,
        }

    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the name of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.name

    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the description of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.description


class NonDuplicableOARepoRequestType(OARepoRequestType):
    """Base request type for OARepo requests that cannot be duplicated.

    This means that on a single topic there can be only one open request of this type.
    """

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: EntityReference,
        topic: Record,
        creator: EntityReference,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created.

        :param identity:        identity of the caller
        :param data:            data of the request
        :param receiver:        receiver of the request
        :param topic:           topic of the request
        :param creator:         creator of the request
        :param args:            additional arguments
        :param kwargs:          additional keyword arguments
        """
        if open_request_exists(topic, self.type_id):
            raise OpenRequestAlreadyExists(self, topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if open_request_exists(topic, cls.type_id):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)
