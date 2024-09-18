from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import AddTopicLinksOnPayloadMixin, OARepoAcceptAction, update_topic


class EditTopicAcceptAction(AddTopicLinksOnPayloadMixin, OARepoAcceptAction):
    self_link = "draft_record:links:self"
    self_html_link = "draft_record:links:self_html"

    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        edit_topic = topic_service.edit(identity, topic["id"], uow=uow)
        update_topic(self.request, topic, edit_topic._record, uow)
        return super().apply(identity, request_type, edit_topic, uow, *args, **kwargs)
