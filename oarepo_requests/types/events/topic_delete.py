#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Topic delete event type."""

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields

from oarepo_requests.types.events.validation import _serialized_topic_validator


class TopicDeleteEventType(EventType):
    """Comment event type."""

    type_id = "D"

    payload_schema = dict(
        topic=fields.Str(validate=[_serialized_topic_validator]),
    )

    payload_required = True
