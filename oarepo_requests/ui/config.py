import inspect

import marshmallow as ma
from flask import current_app
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_runtime.services.custom_fields import CustomFields, InlinedCustomFields
from oarepo_ui.resources.components import AllowedHtmlTagsComponent
from oarepo_ui.resources.config import UIResourceConfig
from oarepo_ui.resources.links import UIRecordLink


def _get_custom_fields_ui_config(key, **kwargs):
    return current_app.config.get(f"{key}_UI", [])


class RequestUIResourceConfig(UIResourceConfig):
    url_prefix = "/requests"
    api_service = "requests"
    blueprint_name = "oarepo_requests_ui"
    template_folder = "templates"
    templates = {
        "detail": "RequestDetail",
    }
    routes = {
        "detail": "/<pid_value>",
    }
    ui_serializer_class = "oarepo_requests.resources.ui.OARepoRequestsUIJSONSerializer"
    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}/{id}"),
    }
    components = [AllowedHtmlTagsComponent]

    error_handlers = {
        PIDDeletedError: "tombstone",
        PIDDoesNotExistError: "not_found",
        PIDUnregistered: "not_found",
        KeyError: "not_found",
        PermissionDeniedError: "permission_denied",
    }

    request_view_args = {"pid_value": ma.fields.Str()}

    @property
    def ui_serializer(self):
        return obj_or_import_string(self.ui_serializer_class)()

    def custom_fields(self, **kwargs):
        api_service = current_service_registry.get(self.api_service)
        # get the record class
        record_class = getattr(api_service, "record_cls", None)
        ui = []
        ret = {
            "ui": ui,
        }
        if not record_class:
            return ret
        # try to get custom fields from the record
        for fld_name, fld in sorted(inspect.getmembers(record_class)):
            if isinstance(fld, InlinedCustomFields):
                prefix = ""
            elif isinstance(fld, CustomFields):
                prefix = fld.key + "."
            else:
                continue

            ui_config = _get_custom_fields_ui_config(fld.config_key, **kwargs)
            if not ui_config:
                continue

            for section in ui_config:
                ui.append(
                    {
                        **section,
                        "fields": [
                            {
                                **field,
                                "field": prefix + field["field"],
                            }
                            for field in section.get("fields", [])
                        ],
                    }
                )
        return ret
