#
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Command Line Interface (CLI) commands for OARepo requests.

This module provides CLI commands for managing OARepo requests,
including request escalation functionality.
"""

from __future__ import annotations

from oarepo_runtime.cli import oarepo

from oarepo_requests.services.escalation import check_escalations


@oarepo.group(name="requests")
def oarepo_requests() -> None:
    """OARepo requests group command."""


@oarepo_requests.command(name="escalate")
def escalate_requests() -> None:
    """Check and escalate all stale requests by changing the recipient and sending the notification to
    the new recipient.

    Stale request is a type of request in which original recipient did not react in time (21 days, 7 days etc.)
    """
    check_escalations()
