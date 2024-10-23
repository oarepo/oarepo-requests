from oarepo_ui.resources.components import UIResourceComponent


class ActionLabelsComponent(UIResourceComponent):
    def form_config(self, *, identity, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")
        action_labels = {}
        for action_type, action in type_.available_actions.items():
            if hasattr(action, "stateful_name"):
                name = action.stateful_name(identity, **kwargs)
            else:
                name = action_type.capitalize()
            action_labels[action_type] = name

        form_config["action_labels"] = action_labels
