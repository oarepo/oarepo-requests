"""Component for adding action labels (button labels) to the request form config."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_ui.resources.components import UIResourceComponent

if TYPE_CHECKING:
    from flask_principal import Identity


class ActionLabelsComponent(UIResourceComponent):
    """Component for adding action labels (button labels) to the request form config."""

    def form_config(
        self,
        *,
        identity: Identity,
        view_args: dict[str, Any],
        form_config: dict,
        **kwargs: Any,
    ) -> None:
        """Add action labels to the form config."""
        type_ = view_args.get("request_type")
        action_labels = {}
        for action_type, action in type_.available_actions.items():
            if hasattr(action, "stateful_name"):
                name = action.stateful_name(identity, **kwargs)
            else:
                name = action_type.capitalize()
            action_labels[action_type] = name

        form_config["action_labels"] = action_labels
