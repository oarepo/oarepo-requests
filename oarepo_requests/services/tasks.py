#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo requests celery tasks."""

from __future__ import annotations

from celery import shared_task

from oarepo_requests.services.escalation import check_escalations


@shared_task(name="escalate-requests")
def escalate_requests_task() -> None:
    """Check and escalate all stale requests."""
    check_escalations()
