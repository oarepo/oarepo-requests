#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Permission generators."""

from __future__ import annotations

from .active import RequestActive
from .conditional import (
    IfNoEditDraft,
    IfNoNewVersionDraft,
    IfRequestedBy,
)

__all__ = (
    "IfNoEditDraft",
    "IfNoNewVersionDraft",
    "IfRequestedBy",
    "RequestActive",
)
