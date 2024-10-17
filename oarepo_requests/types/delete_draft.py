from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from ..actions.delete_draft import DeleteDraftAcceptAction
from ..utils import is_auto_approved, request_identity_matches
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class DeleteDraftRequestType(NonDuplicableOARepoRequestType):
    type_id = "delete_draft"
    name = _("Delete draft")

    dangerous = True

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": DeleteDraftAcceptAction,
        }

    description = _("Request draft deletion")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)

    @override
    def stateful_name(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return _("Request draft deletion")
        match request.status:
            case "submitted":
                return _("Draft deletion requested")
            case _:
                return _("Request draft deletion")

    @override
    def stateful_description(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _("Click to permanently delete the draft.")

        if not request:
            return _("Request permission to delete the draft.")
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Permission to delete draft requested. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "You have been asked to approve the request to permanently delete the draft. "
                        "You can approve or reject the request."
                    )
                return _("Permission to delete draft (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return _("Submit request to get permission to delete the draft.")
