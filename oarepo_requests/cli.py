# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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
