#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for publishing draft requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_access.permissions import system_identity
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import UnitOfWork
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _

from ..notifications.builders.publish import (
    PublishDraftRequestAcceptNotificationBuilder,
    PublishDraftRequestSubmitNotificationBuilder, PublishDraftRequestDeclineNotificationBuilder,
)
from .cascade_events import update_topic
from .generic import (
    AddTopicLinksOnPayloadMixin,
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from .record_snapshot_mixin import RecordSnapshotMixin

if TYPE_CHECKING:
    from flask_principal import Identity
    from .components import RequestActionState
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations.actions import RequestAction


class PublishMixin:
    """Mixin for publish actions."""

    def can_execute(self: RequestAction) -> bool:
        """Check if the action can be executed."""
        if not super().can_execute():  # type: ignore
            return False

        try:
            from ..types.publish_draft import PublishDraftRequestType

            topic = self.request.topic.resolve()
            PublishDraftRequestType.validate_topic(system_identity, topic)
            return True
        except:  # noqa E722: used for displaying buttons, so ignore errors here
            return False


class PublishDraftSubmitAction(PublishMixin, RecordSnapshotMixin, OARepoSubmitAction):
    """Submit action for publishing draft requests."""

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""
        uow.register(
            NotificationOp(
                PublishDraftRequestSubmitNotificationBuilder.build(request=self.request)
            )
        )
        return super().apply(identity, state, uow, *args, **kwargs)


class PublishDraftAcceptAction(
    PublishMixin, AddTopicLinksOnPayloadMixin, OARepoAcceptAction
):
    """Accept action for publishing draft requests."""

    self_link = "published_record:links:self"
    self_html_link = "published_record:links:self_html"

    name = _("Publish")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""
        topic_service = get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")
        id_ = state.topic["id"]

        published_topic = topic_service.publish(
            identity, id_, *args, uow=uow, expand=False, **kwargs
        )
        update_topic(self.request, state.topic, published_topic._record, uow)
        state.topic = published_topic._record
        uow.register(
            NotificationOp(
                PublishDraftRequestAcceptNotificationBuilder.build(request=self.request)
            )
        )
        return super().apply(
            identity, state, uow, *args, **kwargs
        )


class PublishDraftDeclineAction(OARepoDeclineAction):
    """Decline action for publishing draft requests."""

    name = _("Return for correction")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Publish the draft."""
        uow.register(
            NotificationOp(
                PublishDraftRequestDeclineNotificationBuilder.build(request=self.request)
            )
        )
        return super().apply(identity, state, uow, *args, **kwargs)
