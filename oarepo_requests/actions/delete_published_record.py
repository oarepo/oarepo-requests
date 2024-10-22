from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_runtime.i18n import lazy_gettext as _

from .generic import OARepoAcceptAction, OARepoDeclineAction


class DeletePublishedRecordAcceptAction(OARepoAcceptAction):
    name = _("Permanently delete")

    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        topic_service.delete(identity, topic["id"], uow=uow, *args, **kwargs)


class DeletePublishedRecordDeclineAction(OARepoDeclineAction):
    name = _("Keep the record")
