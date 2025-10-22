#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""API views."""

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Blueprint, Flask





def create_notifications(app: Flask) -> Blueprint:  # noqa ARG001
    """Register blueprint routes on app."""
    return Blueprint(
        "oarepo_notifications",
        __name__,
        template_folder=Path(__file__).parent.parent / "templates",
    )
