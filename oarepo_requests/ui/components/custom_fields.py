from oarepo_ui.resources.components import UIResourceComponent


class FormConfigCustomFieldsComponent(UIResourceComponent):
    def form_config(self, *, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")
        form = getattr(type_, "form", None)
        extra_data = getattr(type_, "extra_data", {})
        form_config["extra_data"] = extra_data
        if not form:
            return

        if isinstance(form, dict):
            # it is just a single field
            form = [{"section": "", "fields": [form]}]
        elif isinstance(form, list):
            for it in form:
                if not isinstance(it, dict):
                    raise ValueError(f"Form section must be a dictionary: {it}")
                assert "section" in it, f"Form section must contain 'section' key: {it}"
                assert "fields" in it, f"Form section must contain 'fields' key: {it}"
                assert isinstance(
                    it["fields"], list
                ), f"Form section fields must be a list: {it}"
        else:
            raise ValueError(
                f"form must be either dict containing a definition of a single field or a list of sections: '{form}'. "
                f"See https://inveniordm.docs.cern.ch/customize/metadata/custom_fields/records/#upload-deposit-form "
                f"for details on the format."
            )

        form_config["custom_fields"] = {"ui": form}


class FormConfigRequestTypePropertiesComponent(UIResourceComponent):
    def form_config(self, *, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")

        request_type_properties = {}
        if hasattr(type_, "dangerous"):
            request_type_properties["dangerous"] = type_.dangerous
        if hasattr(type_, "editable"):
            request_type_properties["editable"] = type_.editable
        if hasattr(type_, "has_form"):
            request_type_properties["has_form"] = type_.has_form

        form_config["request_type_properties"] = request_type_properties
