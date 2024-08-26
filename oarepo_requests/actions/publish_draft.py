from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import OARepoAcceptAction


class PublishDraftAcceptAction(OARepoAcceptAction):
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        id_ = topic["id"]

        published_topic = topic_service.publish(
            identity, id_, uow=uow, expand=False, *args, **kwargs
        )

        # add links to the published record
        published_topic_dict = published_topic.to_dict()

        if "payload" not in self.request:
            self.request["payload"] = {}

        # invenio does not allow non-string values in the payload, so using colon notation here
        # client will need to handle this and convert to links structure
        # can not use dot notation as marshmallow tries to be too smart and does not serialize dotted keys
        self.request["payload"]["published_record:links:self"] = published_topic_dict[
            "links"
        ]["self"]
        self.request["payload"]["published_record:links:self_html"] = (
            published_topic_dict["links"]["self_html"]
        )

        return published_topic._record
