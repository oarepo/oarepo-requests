# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Publish draft request type."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from invenio_drafts_resources.records import Draft
from invenio_drafts_resources.records import Record as RecordWithDraft
from invenio_i18n import gettext
from invenio_i18n import lazy_gettext as _
from oarepo_runtime.proxies import current_runtime
from oarepo_runtime.typing import record_from_result

from ..actions.publish_changed_metadata import (
    PublishChangedMetadataAcceptAction,
    PublishChangedMetadataDeclineAction,
    PublishChangedMetadataSubmitAction,
)
from .generic import TopicConvertingRequestType
from .publish_base import PublishRequestType

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.services import RecordService
    from invenio_records_resources.records import Record
    from invenio_requests.records.api import Request


# Incorrectly resolving published record instead of draft in notifications is a known unfixed issue for now.
class PublishChangedMetadataRequestType(PublishRequestType, TopicConvertingRequestType):
    """Request type for publication of changed metadata."""

    type_id = "publish_changed_metadata"
    name = _("Publish changed metadata")

    submit_action = PublishChangedMetadataSubmitAction
    accept_action = PublishChangedMetadataAcceptAction
    decline_action = PublishChangedMetadataDeclineAction

    topic_type = "metadata"

    @override
    def can_create(
        self,
        identity: Identity,
        data: dict,
        receiver: dict[str, str] | Any | None,
        topic: Any,
        creator: dict[str, str] | Any | None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Check if the request can be created."""
        topic = self.convert_topic(identity, topic)
        super().can_create(identity, data, receiver, topic, creator, *args, **kwargs)

    @classmethod
    @override
    def is_applicable_to(cls, identity: Identity, topic: Any, *args: Any, **kwargs: Any) -> bool:
        """Check if the request type is applicable to the topic."""
        try:
            topic = cls.convert_topic(identity, topic)
        except ValueError:
            return False
        return super().is_applicable_to(identity, topic, *args, **kwargs)

    @classmethod
    def convert_topic(cls, identity: Identity, topic: Record) -> Draft:
        """Convert the topic to a draft."""
        if not isinstance(topic, RecordWithDraft):
            raise TypeError(f"Topic type {type(topic)} does not support drafts")
        if isinstance(topic, Draft):
            return topic
        service = cast("RecordService", current_runtime.get_record_service_for_record(topic))
        try:
            return cast("Draft", record_from_result(service.read_draft(identity, topic["id"])))
        except Exception as e:
            raise ValueError(f"Failed to read draft for topic {topic}") from e

    # TODO: used in ui
    @override
    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record | None,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful name of the request."""
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=gettext("Submit for review"),
            create_autoapproved=gettext("Publish changed metadata"),
            submit=gettext("Submit for review"),
            submitted_receiver=gettext("Review and publish changed metadata"),
            submitted_creator=gettext("Changed metadata submitted for review"),
            submitted_others=gettext("Changed metadata submitted for review"),
            accepted=gettext("Accepted changed metadata publication"),
            declined=gettext("Declined changed metadata publication"),
            cancelled=gettext("Cancelled changed metadata publication"),
            created=gettext("Submit for review"),
        )

    @override
    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record | None,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=gettext(
                "By submitting the changed metadata for review you are requesting the publication of the "
                "changed metadata. "
                "The draft will become locked and no further changes will be possible until the request "
                "is accepted or declined. You will be notified about the decision by email."
            ),
            create_autoapproved=gettext(
                "Click to immediately publish the changed metadata. "
                "The draft will be a subject to embargo as requested in the side panel. "
                "Note: The action is irreversible."
            ),
            submit=gettext(
                "Submit for review. After submitting the changed metadata for review, "
                "it will be locked and no further modifications will be possible."
            ),
            submitted_receiver=gettext(
                "The record with changed metadata has been submitted for review. "
                "You can now accept or decline the request."
            ),
            submitted_creator=gettext(
                "The record with changed metadata has been submitted for review. "
                "It is now locked and no further changes are possible. "
                "You will be notified about the decision by email."
            ),
            submitted_others=gettext("The record with changed metadata has been submitted for review. "),
            accepted=gettext("Accepted changed metadata publication"),
            declined=gettext("Declined changed metadata publication"),
            cancelled=gettext("Cancelled changed metadata publication"),
            created=gettext("Waiting for finishing the changed metadata publication request."),
        )
