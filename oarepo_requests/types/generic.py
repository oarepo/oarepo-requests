#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base request type for OARepo requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests.customizations import RequestType
from invenio_requests.customizations.states import RequestState
from invenio_requests.proxies import current_requests_service

from oarepo_requests.errors import OpenRequestAlreadyExistsError
from oarepo_requests.utils import classproperty, open_request_exists

from ..actions.generic import (
    OARepoAcceptAction,
    OARepoCancelAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from ..utils import (
    has_rights_to_accept_request,
    has_rights_to_submit_request,
    is_auto_approved,
    request_identity_matches,
)
from .ref_types import ModelRefTypes, ReceiverRefTypes

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request
    from marshmallow.schema import Schema


class OARepoRequestType(RequestType):
    """Base request type for OARepo requests."""

    description: str = ""

    dangerous = False

    allowed_on_draft = True
    allowed_on_published = True

    editable: bool | None = None
    """Whether the request type can be edited multiple times before it is submitted."""

    allowed_receiver_ref_types = ReceiverRefTypes()  # type: ignore[reportAssignmentType]

    @classproperty
    def has_form(cls) -> bool:  # noqa N805
        """Return whether the request type has a form."""
        return hasattr(cls, "form")

    @classproperty
    def is_editable(cls) -> bool:  # noqa N805
        """Return whether the request type is editable."""
        if cls.editable is not None:
            return cls.editable
        return cls.has_form

    @classproperty
    def available_statuses(cls) -> dict[str, RequestState]:  # type: ignore[reportIncompatibleVariableOverride] # noqa N805
        """Return available statuses for the request type.

        The status (open, closed, undefined) are used for request filtering.
        """
        return {**super().available_statuses, "created": RequestState.OPEN}

    @classmethod
    def _create_marshmallow_schema(cls) -> type[Schema]:
        """Create a marshmallow schema for this request type with required payload field."""
        schema = super()._create_marshmallow_schema()
        # TODO: idk why .fields
        if (
            cls.payload_schema is not None
            and hasattr(schema, "fields")
            and "payload" in schema.fields
        ):  # type: ignore[reportAttributeAccessIssue]
            schema.fields["payload"].required = True  # type: ignore[reportAttributeAccessIssue]

        return cast("type[Schema]", schema)

    def can_create(
        self,
        identity: Identity,
        data: dict[str, Any],  # noqa ARG002
        receiver: dict[str, str],  # noqa ARG002
        topic: Record,
        creator: dict[str, str],  # noqa ARG002
        *args: Any,  # noqa ARG002
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
    ) -> bool:  # noqa ARG002
        """Check if the request type is applicable to the topic.

        Used for checking whether there is any situation where the client can create
        a request of this type it's different to just using can create with no receiver
        and data because that checks specifically for situation without them while this
        method is used to check whether there is a possible situation a user might create
        this request eg. for the purpose of serializing a link on associated record
        """
        return cast(
            "bool",
            current_requests_service.check_permission(
                identity, "create", record=topic, request_type=cls, **kwargs
            ),
        )

    @classproperty
    def available_actions(  # type: ignore[reportIncompatibleVariableOverride]
        self,
    ) -> dict[str, type[RequestAction]]:
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": OARepoSubmitAction,
            "accept": OARepoAcceptAction,
            "decline": OARepoDeclineAction,
            "cancel": OARepoCancelAction,
        }

    # TODO: move these to RecordRequestType too?
    def stateful_name(
        self,
        identity: Identity,  # noqa ARG002
        *,
        topic: Record,  # noqa ARG002
        request: Request | None = None,  # noqa ARG002
        **kwargs: Any,  # noqa ARG002
    ) -> str | LazyString:
        """Return the name of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.name

    def stateful_description(
        self,
        identity: Identity,  # noqa ARG002
        *,
        topic: Record,  # noqa ARG002
        request: Request | None = None,  # noqa ARG002
        **kwargs: Any,  # noqa ARG002
    ) -> str | LazyString:
        """Return the description of the request that reflects its current state.

        :param identity:        identity of the caller
        :param request:         the request
        :param topic:           resolved request's topic
        """
        return self.description

    def string_by_state(  # noqa C901, PLR0913, PLR0911
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        # strings
        create: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        create_autoapproved: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submit: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_receiver: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_creator: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        submitted_others: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        accepted: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        declined: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        cancelled: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
        created: (
            str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString]
        ),
    ) -> str | LazyString:
        """Return a string that varies by the state of the request.

        :param create:        string to be used on request type if user can create a request
        :param create_autoapproved: string to be used on request type if user can create a request
                                    and the request is auto approved
        :param submit:        string to be used on request type if user can submit a request
        :param accept_decline: string to be used on request type if user can accept or decline a request
        :param view:          string to be used on request type if user can view a request
        """

        def get_string(
            string: str
            | LazyString
            | Callable[[Identity, Record, Request | None], str | LazyString],
            identity: Identity,
            topic: Record,
            request: Request | None = None,
        ) -> str | LazyString:
            if callable(string):
                return string(identity, topic, request)
            return string

        if request:
            match request.status:
                case "submitted":
                    if has_rights_to_accept_request(request, identity):
                        return get_string(submitted_receiver, identity, topic, request)
                    if request_identity_matches(request.created_by, identity):
                        return get_string(submitted_creator, identity, topic, request)
                    return get_string(submitted_others, identity, topic, request)
                case "accepted":
                    return get_string(accepted, identity, topic, request)
                case "declined":
                    return get_string(declined, identity, topic, request)
                case "cancelled":
                    return get_string(cancelled, identity, topic, request)
                case "created":
                    if has_rights_to_submit_request(request, identity):
                        return get_string(submit, identity, topic, request)
                    return get_string(created, identity, topic, request)
                case _:
                    return (
                        f'Unknown label for status "{request.status}" in "{__file__}"'
                    )

        if is_auto_approved(self, identity=identity, topic=topic):
            return get_string(create_autoapproved, identity, topic, request)
        return get_string(create, identity, topic, request)


class OARepoRecordRequestType(OARepoRequestType):
    """Base request type for OARepo requests that can be created on a record."""

    allowed_topic_ref_types = ModelRefTypes()  # type: ignore[reportAssignmentType]

    @classmethod
    def _allowed_by_publication_status(cls, record: Record) -> bool:
        if not hasattr(record, "publication_status"):
            return bool(cls.allowed_on_published)
        return bool(
            (cls.allowed_on_draft and record.publication_status == "draft")  # type: ignore[reportAttributeAccessIssue]
            or (cls.allowed_on_published and record.publication_status == "published")  # type: ignore[reportAttributeAccessIssue]
        )

    def can_create(
        self,
        identity: Identity,
        data: dict[str, Any],
        receiver: dict[str, str],
        topic: Record,
        creator: dict[str, str],
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
        if not self._allowed_by_publication_status(record=topic):
            raise PermissionDeniedError("create")
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

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
        if not cls._allowed_by_publication_status(record=topic):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)


class NonDuplicableOARepoRecordRequestType(OARepoRecordRequestType):
    """Base request type for OARepo requests that cannot be duplicated.

    This means that on a single topic there can be only one open request of this type.
    """

    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: dict[str, str],
        topic: Record,
        creator: dict[str, str],
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
            raise OpenRequestAlreadyExistsError(self, topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if open_request_exists(topic, cls.type_id):
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)
