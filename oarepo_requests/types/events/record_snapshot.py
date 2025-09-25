#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Record snapshot event type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields

if TYPE_CHECKING:
    from typing import ClassVar

    import marshmallow as ma


class RecordSnapshotEventType(EventType):
    """Record snapshot event type.

    Payload contain old version of the record, new version and their difference.
    """

    type_id = "S"

    payload_schema: ClassVar[dict[str, ma.fields.Field]] = {
        "old_version": fields.Str(),
        "new_version": fields.Str(),
        "diff": fields.Str(),
    }

    payload_required = True
