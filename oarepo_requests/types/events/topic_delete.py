#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Topic delete event type."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields

from oarepo_requests.types.events.validation import _serialized_topic_validator

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    import marshmallow as ma


class TopicDeleteEventType(EventType):
    """Comment event type."""

    type_id = "D"

    payload_schema: ClassVar[Mapping[str, ma.fields.Field] | Callable[[], Mapping[str, fields.Field]] | None] = {  # type: ignore[reportIncompatibleVariableOverride]
        "topic": fields.Str(validate=[_serialized_topic_validator]),
    }

    payload_required = True
