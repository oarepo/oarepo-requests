# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Request needs."""

from __future__ import annotations

from invenio_access.permissions import SystemRoleNeed

request_active = SystemRoleNeed("request")
"""Need that is added to identity whenever a request is being handled (inside the 'accept' action)."""
