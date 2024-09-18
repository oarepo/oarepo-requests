from invenio_requests.customizations.event_types import EventType
from marshmallow import fields, validate


class TopicUpdateEventType(EventType):
    """Comment event type."""

    type_id = "T"

    def payload_schema():
        """Return payload schema as a dictionary."""
        # we need to import here because of circular imports
        from invenio_requests.records.api import RequestEventFormat

        return dict(
            old_topic=fields.Str(),
            new_topic=fields.Str(),
            # content=utils_fields.SanitizedHTML(
            #    required=True, validate=validate.Length(min=1)
            # ),
            format=fields.Str(
                validate=validate.OneOf(choices=[e.value for e in RequestEventFormat]),
                load_default=RequestEventFormat.HTML.value,
            ),
        )

    payload_required = True
