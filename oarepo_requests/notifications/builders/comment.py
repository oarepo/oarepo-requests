from invenio_notifications.services.generators import EntityResolve
from invenio_requests.notifications.builders import (
    CommentRequestEventCreateNotificationBuilder as InvenioCommentRequestEventCreateNotificationBuilder,
)
from invenio_requests.notifications.generators import RequestParticipantsRecipient

from oarepo_requests.notifications.generators import GeneralRequestParticipantsRecipient
from oarepo_requests.utils import classproperty


class CommentRequestEventCreateNotificationBuilder(InvenioCommentRequestEventCreateNotificationBuilder):
    @classproperty
    def context(self):
        return *super().context, EntityResolve(key="request.topic")

    @classproperty
    def recipients(self):
        recipients = super().recipients
        for receiver in recipients:
            if isinstance(receiver, RequestParticipantsRecipient):
                recipients.remove(receiver)
                recipients.append(GeneralRequestParticipantsRecipient(key="request"))
                break
        return recipients


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

        for r in CommentRequestEventCreateNotificationBuilder.context:
            if isinstance(r, EntityResolve) and r.key == "request.topic":
                break
        else:
            CommentRequestEventCreateNotificationBuilder.context.append(
                EntityResolve(key="request.topic"),
            )


        for r in CommentRequestEventCreateNotificationBuilder.recipients:
            if isinstance(r, RequestParticipantsRecipient):
                CommentRequestEventCreateNotificationBuilder.recipients.remove(r)
                CommentRequestEventCreateNotificationBuilder.recipients.append(OARepoRequestParticipantsRecipient(key="request"))
                break

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
