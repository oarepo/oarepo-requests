from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import AddTopicLinksOnPayloadMixin, OARepoAcceptAction


class PublishDraftAcceptAction(AddTopicLinksOnPayloadMixin, OARepoAcceptAction):
    self_link = "published_record:links:self"
    self_html_link = "published_record:links:self_html"

    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        id_ = topic["id"]

        published_topic = topic_service.publish(
            identity, id_, uow=uow, expand=False, *args, **kwargs
        )

        return super().apply(
            identity, request_type, published_topic, uow, *args, **kwargs
        )
