#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Request escalation event type."""

from __future__ import annotations

import marshmallow as ma
from invenio_requests.customizations.event_types import EventType
from marshmallow import fields


class EscalationEventType(EventType):
    """Comment event type."""

    type_id = "E"
    payload_required = True

    @staticmethod
    def payload_schema() -> dict[str, ma.fields.Field]:
        """Return payload schema as a dictionary."""
        return {
            "old_receiver": fields.Str(),
            "new_receiver": fields.Str(),
            "escalation": fields.Str(),
        }
