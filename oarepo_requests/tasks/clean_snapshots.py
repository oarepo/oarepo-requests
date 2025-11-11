#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Task for cleaning old snapshots."""

from __future__ import annotations

import datetime

from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_requests.records.models import RequestMetadata

from oarepo_requests.models import RecordSnapshot


@shared_task
def clean_snapshots() -> None:
    """Clean old snapshots from record_snapshots table where their request was accepted.

    By default is 365 days old snapshot are deleted.
    """
    days = current_app.config.get("SNAPSHOT_CLEANUP_DAYS", 365)

    cutoff_date = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=days)

    accepted_requests = (
        db.session.query(RequestMetadata.id).filter(RequestMetadata.json["type"] == "accepted").subquery()
    )

    db.session.query(RecordSnapshot).filter(
        RecordSnapshot.id.in_(accepted_requests), RecordSnapshot.created < cutoff_date
    ).delete(synchronize_session="fetch")

    db.session.commit()
