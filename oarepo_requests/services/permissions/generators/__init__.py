# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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
