from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_rdm_records.requests.access.requests import UserAccessRequest
from .generic import OARepoRequestType
from typing_extensions import override

from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_runtime.datastreams.utils import get_record_service_for_record

if TYPE_CHECKING:
    from flask_babel.speaklater import LazyString
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.records.api import Request


class OARepoUserAccessRequestType(UserAccessRequest, OARepoRequestType):
    """Request access request type."""

    type_id = "request_user_access"

    form = [
        {
            "section": "",
            "fields": [
                {
                    "field": "permission",
                    "ui_widget": "Dropdown",
                    "props": {
                        "label": _("Permission"),
                        "placeholder": _("Edit or view"),
                        "options": [
                            {"id": "edit", "title_l10n": _("Edit")},
                            {"id": "view", "title_l10n": _("View")},
                        ],
                        "required": True,
                    },
                },
                {
                    "section": "",
                    "field": "message",
                    "ui_widget": "RichInput",
                    "props": {
                        "label": _("Message"),
                        "placeholder": _("Write down the reason to request access."),
                        "required": False,
                    },
                },
            ],
        }
    ]

    @classmethod
    def is_applicable_to(
        cls, identity: Identity, topic: Record, *args: Any, **kwargs: Any
    ) -> bool:
        """Check if the request type is applicable to the topic."""
        if topic.access.status.value == "restricted":
            topic_service = get_record_service_for_record(topic)
            return not topic_service.check_permission(
                identity, "read_files", record=topic
            )

        return False
    
    
        
    @override
    def stateful_name(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful name of the request."""
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=_("Access request"),
            create_autoapproved=_("Access request"),
            submit=_("Access request"),
            submitted_receiver=_("Access request"),
            submitted_creator=_("Access requested"),
            submitted_others=_("Access requested"),
            accepted=_("Access has been granted"),
            declined=_("Access has been declined"),
            cancelled=_("Access request has been canceled"),
            created=_("Access request pending"),
        )

    @override
    def stateful_description(
        self,
        identity: Identity,
        *,
        topic: Record,
        request: Request | None = None,
        **kwargs: Any,
    ) -> str | LazyString:
        """Return the stateful description of the request."""
        return self.string_by_state(
            identity=identity,
            topic=topic,
            request=request,
            create=_(
                "You are requesting access to view or edit files of a restricted record. "
                "You will be notified about the decision by email."
            ),
            create_autoapproved=_(
                "Click to immediately get access to view or edit files of a restricted record."
            ),
            submit=_("Request access to access the files of this restricted record."),
            submitted_receiver=_(
                "Access request to for a restricted record is available. "
                "You can now accept or decline the request."
            ),
            submitted_creator=_(
                "You have submitted an access request to access files of the restricted record. "
                "You will be notified about the decision by email."
            ),
            submitted_others=_(
                "An access request to view or edit files of a restricted record has been submitted."
            ),
            accepted=_(
                "Your access request has been accepted. You can now access the restricted files."
            ),
            declined=_(
                "Your access request has been declined. "
            ),
            cancelled=_(
                "Your access request has been canceled."
            ),
            created=_("Waiting for finishing the access request."),
        )
