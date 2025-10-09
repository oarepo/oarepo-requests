#
# Copyright (C) 2024 CESNET z.s.p.o.
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


@oarepo.group(name="requests")
def oarepo_requests() -> None:
    """OARepo requests group command."""


# TODO: escalate_requests
