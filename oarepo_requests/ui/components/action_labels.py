#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Component for adding action labels (button labels) to the request form config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_requests.customizations import RequestType


class ActionLabelsComponent(UIResourceComponent):
    """Component for adding action labels (button labels) to the request form config."""

    def form_config(
        self,
        *,
        identity: Identity,
        form_config: dict,
        request_type: RequestType,
        **kwargs: Any,
    ) -> None:
        """Add action labels to the form config."""
        action_labels = {}
        if request_type:
            for action_type, action in request_type.available_actions.items():
                if hasattr(action, "stateful_name"):
                    name = action.stateful_name(identity, **kwargs)
                else:
                    name = action_type.capitalize()
                action_labels[action_type] = name

        form_config["action_labels"] = action_labels
