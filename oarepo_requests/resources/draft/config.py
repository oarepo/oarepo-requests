#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration of the draft record requests resource."""

from __future__ import annotations

import importlib_metadata

from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """Configuration of the draft record requests resource."""

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests-draft": "/<pid_value>/draft/requests",
        "request-type-draft": "/<pid_value>/draft/requests/<request_type>",
    }

    @property
    def error_handlers(self) -> dict:
        """Return error handlers loaded dynamically from entry points."""
        parent_handlers = (
            super().error_handlers if hasattr(super(), "error_handlers") else {}
        )
        handlers = parent_handlers.copy() if parent_handlers else {}

        for entry_point in importlib_metadata.entry_points(
            group="invenio.documents.error_handlers"
        ):
            exception_class, handler = entry_point.load()()
            handlers[exception_class] = handler
        return handlers
