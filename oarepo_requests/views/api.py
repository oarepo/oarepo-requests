# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""API views."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask


def create_notifications(_app: Flask) -> Blueprint:
    """Register blueprint routes on app."""
    return Blueprint(
        "oarepo_notifications",
        __name__,
        template_folder=Path(__file__).parent.parent / "templates",
    )
