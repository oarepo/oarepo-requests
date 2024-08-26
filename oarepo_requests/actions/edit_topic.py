from oarepo_runtime.datastreams.utils import get_record_service_for_record

from .generic import OARepoAcceptAction


class EditTopicAcceptAction(OARepoAcceptAction):
    def apply(self, identity, request_type, topic, uow, *args, **kwargs):
        topic_service = get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        edit_topic = topic_service.edit(identity, topic["id"], uow=uow)

        # add links to the draft (edited) record
        edit_topic_dict = edit_topic.to_dict()

        if "payload" not in self.request:
            self.request["payload"] = {}

        # invenio does not allow non-string values in the payload, so using colon notation here
        # client will need to handle this and convert to links structure
        # can not use dot notation as marshmallow tries to be too smart and does not serialize dotted keys
        self.request["payload"]["draft_record:links:self"] = edit_topic_dict[
            "links"
        ]["self"]
        self.request["payload"]["draft_record:links:self_html"] = (
            edit_topic_dict["links"]["self_html"]
        )

        return edit_topic._record

