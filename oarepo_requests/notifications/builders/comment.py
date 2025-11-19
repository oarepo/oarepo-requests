#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo notification builders for comment event notification."""

from __future__ import annotations

from invenio_notifications.services.generators import ContextGenerator, EntityResolve, RecipientGenerator
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder as InvenioCommentRequestEventCreateNotificationBuilder,
)
from invenio_requests.notifications.generators import RequestParticipantsRecipient

from oarepo_requests.notifications.generators import GeneralRequestParticipantsRecipient, RequestEntityResolve
from oarepo_requests.utils import classproperty


class CommentRequestEventCreateNotificationBuilder(InvenioCommentRequestEventCreateNotificationBuilder):
    """Notification builder for comment event."""

    # "classproperty[tuple[ContextGenerator, ...]]" is not assignable to "List[ContextGenerator]"

    @classproperty
    def context(self) -> tuple[ContextGenerator, ...]:  # type: ignore[reportIncompatibleVariableOverride]
        """Get context for the notification builder."""
        invenio = super().context
        for idx, r in enumerate(list(invenio)):
            if isinstance(r, EntityResolve) and r.key == "request":
                invenio[idx] = (
                    # entity resolver that adds the correct title if it is missing
                    RequestEntityResolve(
                        key="request",
                    )
                )
                break
        return *invenio, EntityResolve(key="request.topic")

    @classproperty
    def recipients(self) -> tuple[RecipientGenerator, ...]:  # type: ignore[reportIncompatibleVariableOverride]
        """Get recipients for the notification builder."""
        invenio = super().recipients
        for idx, r in enumerate(list(invenio)):
            if isinstance(r, RequestParticipantsRecipient):
                invenio[idx] = GeneralRequestParticipantsRecipient(key="request")
                break
        return tuple(invenio)
