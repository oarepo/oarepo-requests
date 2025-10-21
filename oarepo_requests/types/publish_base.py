#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, override

import marshmallow as ma
from invenio_drafts_resources.records import Record as RecordWithDraft
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _

from oarepo_requests.actions.publish_draft import (
    PublishDraftAcceptAction,
    PublishDraftDeclineAction,
    PublishDraftSubmitAction,
)

from ..temp_utils import get_draft_record_service, search_requests
from ..utils import classproperty
from .generic import NonDuplicableOARepoRequestType

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction
    from invenio_requests.records.api import Request


from invenio_access.permissions import system_identity
from invenio_requests.records.api import Request

from ..errors import UnresolvedRequestsError


class PublishRequestType(NonDuplicableOARepoRequestType):
    """Publish draft request type."""

    allowed_on_published = True

    @classproperty
    def available_actions(cls) -> dict[str, type[RequestAction]]:  # noqa N805
        """Return available actions for the request type."""
        return {
            **super().available_actions,
            "submit": PublishDraftSubmitAction,
            "accept": PublishDraftAcceptAction,
            "decline": PublishDraftDeclineAction,
        }

    description = _("Request to publish a draft")  # type: ignore[reportAssignmentType]
    receiver_can_be_none = True

    editable = False

    def assert_no_pending_requests(
        self,
        topic: Record,
    ) -> None:
        """Assert that there are no pending requests on the topic."""
        requests = search_requests(system_identity, topic)

        for result in requests._results:  # noqa SLF001
            # note: we can not use solely the result.is_open because changes may not be committed yet
            # to opensearch index. That's why we need to get the record from DB and re-check.
            if (
                result.is_open
                and result.type != self.type_id
                and Request.get_record(result.uuid)["status"]
                in (
                    "submitted",
                    "created",
                )
            ):
                raise UnresolvedRequestsError(action=str(self.name))

    @override
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
        """Check if the request can be created."""
        if not isinstance(topic, RecordWithDraft):
            raise TypeError(f"Topic type {type(topic)} does not support drafts")
        self.assert_no_pending_requests(topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)
        self.validate_topic(identity, topic)

    @classmethod
    def validate_topic(cls, identity: Identity, topic: Record) -> None:
        """Validate the topic.

        :param: identity: identity of the caller
        :param: topic: topic of the request

        :raises: ValidationError: if the topic is not valid
        """
        topic_service = get_draft_record_service(topic)
        topic_service.validate_draft(identity, topic["id"])

        # if files support is enabled for this topic, check if there are any files
        if hasattr(topic, "files"):
            can_toggle_files = topic_service.check_permission(identity, "manage_files", record=topic)
            draft_files = topic.files  # type: ignore[reportAttributeAccessIssue]
            if draft_files.enabled and not draft_files.items():
                if can_toggle_files:
                    my_message = gettext(
                        "Missing uploaded files. To disable files for this record please mark it as metadata-only."
                    )
                else:
                    my_message = gettext("Missing uploaded files.")

                raise ma.ValidationError({"files.enabled": [my_message]})

    @classmethod
    @override
    def is_applicable_to(cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any) -> bool:
        """Check if the request type is applicable to the topic."""
        if not isinstance(topic, RecordWithDraft):
            raise TypeError(f"Topic type {type(topic)} does not support drafts")
        return super().is_applicable_to(identity, topic, *args, **kwargs)

    @classmethod
    def topic_type(cls, topic: Record) -> Literal["initial", "new_version", "metadata", "published"]:
        """Return publish status type of the topic."""
        if not isinstance(topic, RecordWithDraft):
            raise TypeError(f"Topic type {type(topic)} does not support drafts")
        index = topic.versions.index
        is_latest = topic.versions.is_latest
        is_draft = topic.is_draft

        if not is_draft:
            return "published"

        if index == 1 and not is_latest:
            return "initial"
        if index > 1 and not is_latest:
            return "new_version"
        return "metadata"
