#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Component for adding requests UI configuration to the form config."""

from __future__ import annotations

from typing import Any

from flask import current_app
from oarepo_ui.resources.components import UIResourceComponent


class RequestsUIConfigComponent(UIResourceComponent):
    """Component for adding requests UI configuration to the form config."""

    def form_config(
        self,
        *,
        form_config: dict,
        **kwargs: Any,
    ) -> None:
        """Add requests UI configuration to the form config."""
        form_config["requests_ui_config"] = {
            "allowGroupReviewers": current_app.config.get("USERS_RESOURCES_GROUPS_ENABLED", False),
            "enableReviewers": current_app.config.get("REQUESTS_REVIEWERS_ENABLED", False),
            "maxReviewers": current_app.config.get("REQUESTS_REVIEWERS_MAX_NUMBER", 10),
        }
