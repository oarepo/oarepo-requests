from oarepo_runtime.i18n import lazy_gettext as _
from typing_extensions import override

from oarepo_requests.actions.delete_topic import DeleteTopicAcceptAction

from ..utils import is_auto_approved, request_identity_matches
from .generic import NonDuplicableOARepoRequestType
from .ref_types import ModelRefTypes


class DeletePublishedRecordRequestType(NonDuplicableOARepoRequestType):
    type_id = "delete_published_record"
    name = _("Delete record")

    @classmethod
    @property
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": DeleteTopicAcceptAction,
        }

    description = _("Request deletion of published record")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=False)

    @override
    def stateful_name(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return self.name
        if not request:
            return _("Request record deletion")
        match request.status:
            case "submitted":
                return _("Record deletion requested")
            case _:
                return _("Request record deletion")

    @override
    def stateful_description(self, identity, *, topic=None, request=None):
        if is_auto_approved(self, identity=identity, topic=topic):
            return _("Click to permanently delete the record.")

        if not request:
            return _("Request permission to delete the record.")
        match request.status:
            case "submitted":
                if request_identity_matches(request.created_by, identity):
                    return _(
                        "Permission to delete record requested. "
                        "You will be notified about the decision by email."
                    )
                if request_identity_matches(request.receiver, identity):
                    return _(
                        "You have been asked to approve the request to permanently delete the record. "
                        "You can approve or reject the request."
                    )
                return _("Permission to delete record (including files) requested. ")
            case _:
                if request_identity_matches(request.created_by, identity):
                    return _("Submit request to get permission to delete the record.")
