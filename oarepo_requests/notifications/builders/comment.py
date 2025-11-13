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

from oarepo_requests.notifications.generators import GeneralRequestParticipantsRecipient
from oarepo_requests.utils import classproperty


class CommentRequestEventCreateNotificationBuilder(InvenioCommentRequestEventCreateNotificationBuilder):
    """Notification builder for comment event."""

    # "classproperty[tuple[ContextGenerator, ...]]" is not assignable to "List[ContextGenerator]"

    @classproperty
    def context(self) -> tuple[ContextGenerator, ...]:  # type: ignore[reportIncompatibleVariableOverride]
        """Get context for the notification builder."""
        return *super().context, EntityResolve(key="request.topic")

    @classproperty
    def recipients(self) -> tuple[RecipientGenerator, ...]:  # type: ignore[reportIncompatibleVariableOverride]
        """Get recipients for the notification builder."""
        recipients = super().recipients
        for receiver in recipients:
            if isinstance(receiver, RequestParticipantsRecipient):
                recipients.remove(receiver)
                recipients.append(GeneralRequestParticipantsRecipient(key="request"))
                break
        return tuple(recipients)


# TODO: if anything remaining in this is useful?
"""
def override_invenio_notifications(
    state: BlueprintSetupState, *args: Any, **kwargs: Any
) -> None:
    with state.app.app_context():
        from invenio_notifications.services.generators import EntityResolve
        from invenio_requests.notifications.builders import (
            CommentRequestEventCreateNotificationBuilder,
        )

        from oarepo_requests.notifications.generators import RequestEntityResolve




        for idx, r in list(
            enumerate(CommentRequestEventCreateNotificationBuilder.context)
        ):
            if isinstance(r, EntityResolve) and r.key == "request":
                CommentRequestEventCreateNotificationBuilder.context[idx] = (
                    # entity resolver that adds the correct title if it is missing
                    RequestEntityResolve(
                        key="request",
                    )
                )

        from invenio_notifications.tasks import (
            dispatch_notification,
        )

        original_delay = dispatch_notification.delay

        def i18n_enabled_notification_delay(backend, recipient, notification):
            locale = None
            if isinstance(recipient, dict):
                locale = recipient.get("data", {}).get("preferences", {}).get("locale")
            locale = locale or current_app.config.get("BABEL_DEFAULT_LOCALE", "en")
            with force_locale(locale):
                notification = resolve_lazy_strings(notification)
            return original_delay(backend, recipient, notification)

        dispatch_notification.delay = i18n_enabled_notification_delay
"""
