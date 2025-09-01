#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_requests.customizations.event_types import EventType
from marshmallow import fields


class RecordSnapshotEventType(EventType):
    """Record snapshot event type.

    Payload contain old version of the record, new version and their difference.
    """

    type_id = "S"

    payload_schema = {"old_version": fields.Str(), "new_version": fields.Str(), "diff": fields.Str()}

    payload_required = True
