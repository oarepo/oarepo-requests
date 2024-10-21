from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .cascade_events import update_topic
from .generic import AddTopicLinksOnPayloadMixin, OARepoAcceptAction


class NewVersionAcceptAction(AddTopicLinksOnPayloadMixin, OARepoAcceptAction):
    self_link = "draft_record:links:self"
    self_html_link = "draft_record:links:self_html"

    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        new_version_topic = topic_service.new_version(identity, topic["id"], uow=uow)
        update_topic(self.request, topic, new_version_topic._record, uow)
        return super().apply(
            identity, request_type, new_version_topic, uow, *args, **kwargs
        )
