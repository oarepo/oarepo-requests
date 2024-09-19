from invenio_requests import current_request_type_registry
from oarepo_ui.resources.components import UIResourceComponent

"""
form = [
        {
            "field": "version",
            "ui_widget": "Input",
            "props": {
                "label": _("Resource version"),
                "placeholder": _("Write down the version (first, second…)."),
                "required": False,
            },
        }
    ]

"""


class FormConfigCustomFieldsComponent(UIResourceComponent):

    def form_config(self, *, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")
        type_ = current_request_type_registry.lookup(type_, quiet=True)
        if hasattr(type_, "form"):
            form = type_.form
            form_config["custom_fields"] = {"ui": {"fields": form}}
