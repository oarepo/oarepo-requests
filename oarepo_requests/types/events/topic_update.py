from invenio_requests.customizations.event_types import EventType
from marshmallow import fields, validate

def _serialized_topic_validator(value):
    if len(value.split('.')) != 2:
        raise ValueError("Serialized topic must be a string with model and id separated by a single dot.")
    return value


class TopicUpdateEventType(EventType):
    """Comment event type."""

    type_id = "T"

    payload_schema = dict(
        old_topic=fields.Str(validate=[_serialized_topic_validator]),
        new_topic=fields.Str(validate=[_serialized_topic_validator]),
    )

    payload_required = True
