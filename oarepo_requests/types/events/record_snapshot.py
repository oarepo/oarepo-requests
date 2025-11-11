#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Record snapshot event type."""

from __future__ import annotations

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields


class RecordSnapshotEventType(EventType):
    """Record snapshot event type.

    Payload contain old version of the record, new version and their difference.
    """

    type_id = "S"

    @staticmethod
    def payload_schema() -> dict[str, fields.Field]:
        """Return schema for the event payload."""
        return {"old_version": fields.Str(), "new_version": fields.Str(), "diff": fields.Str()}

    payload_required = True
