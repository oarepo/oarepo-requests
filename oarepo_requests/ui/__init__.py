#
# Copyright (c) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo requests UI package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oarepo_requests.ui.overrides import register_request_ui_overrides

if TYPE_CHECKING:
    from flask import Flask


def finalize_app(app: Flask) -> None:  # noqa: ARG001  # pragma: no cover
    """Register per-request-type Label/Icon React overrides on every page that renders request UIs."""
    register_request_ui_overrides()
