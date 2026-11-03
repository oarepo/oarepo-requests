# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo notification builders for comment event notification."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_notifications.services.generators import (
    ContextGenerator,
    EntityResolve,
    RecipientGenerator,
)
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder as InvenioCommentRequestEventCreateNotificationBuilder,
)
from invenio_requests.notifications.generators import RequestParticipantsRecipient

from oarepo_requests.notifications.filters import UsersWithNoMailRecipientFilter
from oarepo_requests.notifications.generators import (
    GeneralRequestParticipantsRecipient,
    RequestEntityResolve,
)
from oarepo_requests.notifications.generators.context import ReferenceSavingEntityResolve

if TYPE_CHECKING:
    from collections.abc import Sequence

    from invenio_notifications.services.filters import RecipientFilter


def _oarepo_context_generator(generator: ContextGenerator) -> ContextGenerator:
    if not isinstance(generator, EntityResolve):
        return generator
    if generator.key == "request":
        return RequestEntityResolve(key=generator.key)
    return ReferenceSavingEntityResolve(key=generator.key)


class CommentRequestEventCreateNotificationBuilder(InvenioCommentRequestEventCreateNotificationBuilder):
    """Notification builder for comment event."""

    context: Sequence[ContextGenerator] = (
        *map(_oarepo_context_generator, InvenioCommentRequestEventCreateNotificationBuilder.context),
        ReferenceSavingEntityResolve(key="request.topic"),
    )

    recipients: Sequence[RecipientGenerator] = tuple(
        GeneralRequestParticipantsRecipient(key="request") if isinstance(r, RequestParticipantsRecipient) else r
        for r in InvenioCommentRequestEventCreateNotificationBuilder.recipients
    )

    recipient_filters: Sequence[RecipientFilter] = (
        *InvenioCommentRequestEventCreateNotificationBuilder.recipient_filters,
        UsersWithNoMailRecipientFilter(),
    )
