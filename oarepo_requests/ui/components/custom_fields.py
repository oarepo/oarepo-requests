from oarepo_ui.resources.components import UIResourceComponent


class FormConfigCustomFieldsComponent(UIResourceComponent):

    def form_config(self, *, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")
        if hasattr(type_, "form"):
            form = type_.form
            form_config["custom_fields"] = {"ui": {"fields": form}}
