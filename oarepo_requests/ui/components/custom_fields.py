from oarepo_ui.resources.components import UIResourceComponent


class FormConfigCustomFieldsComponent(UIResourceComponent):

    def form_config(self, *, view_args, form_config, **kwargs):
        type_ = view_args.get("request_type")
        form = getattr(type_, "form", None)
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
