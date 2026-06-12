#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from oarepo_ui.proxies import current_ui_overrides

from oarepo_requests.ui.overrides import (
    REQUEST_TYPE_ICONS,
    REQUEST_TYPE_LABELS,
    REQUESTS_UI_ENDPOINTS,
)


def test_request_ui_overrides_registered(app):
    """Every request type gets a Label and Icon override on every request UI endpoint."""
    with app.app_context():
        registered = {(o.endpoint, o.overridable_id) for o in current_ui_overrides}

    for endpoint in REQUESTS_UI_ENDPOINTS:
        for type_id in REQUEST_TYPE_LABELS:
            assert (endpoint, f"RequestTypeLabel.layout.{type_id}") in registered
        for type_id in REQUEST_TYPE_ICONS:
            assert (endpoint, f"InvenioRequests.RequestTypeIcon.layout.{type_id}") in registered
