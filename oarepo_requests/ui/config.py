#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Config for the UI resources."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import marshmallow as ma
from flask import current_app

# TODO: temp
from flask_resources import ResourceConfig
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_request_type_registry
from oarepo_ui.resources.components import AllowedHtmlTagsComponent

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask_resources.serializers.base import BaseSerializer
    from invenio_records_resources.records import Record
    from invenio_requests.customizations.request_types import RequestType


def _get_custom_fields_ui_config(key: str, **kwargs: Any) -> list[dict]:  # noqa ARG001
    return current_app.config.get(f"{key}_UI", [])


class RequestTypeSchema(ma.fields.Str):
    """Schema that makes sure that the request type is a valid request type."""

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> RequestType:
        """Deserialize the value and check if it is a valid request type."""
        ret = super()._deserialize(value, attr, data, **kwargs)
        return current_request_type_registry.lookup(ret, quiet=True)


"""
class RequestsFormConfigResourceConfig(FormConfigResourceConfig):
    url_prefix = "/requests"
    blueprint_name = "oarepo_requests_form_config"
    components = [
        AllowedHtmlTagsComponent,
        FormConfigCustomFieldsComponent,
        FormConfigRequestTypePropertiesComponent,
        ActionLabelsComponent,
    ]
    request_view_args = {"request_type": RequestTypeSchema()}
    routes = {
        "form_config": "/configs/<request_type>",
    }
"""


class UIResourceConfig(ResourceConfig):
    """Base resource config for the UI."""

    components = None
    template_folder = None

    def get_template_folder(self) -> str | None:
        """Get the template folder."""
        if not self.template_folder:
            return None

        tf = Path(self.template_folder)
        if not tf.is_absolute():
            tf = Path(inspect.getfile(type(self))).parent.absolute().joinpath(tf).absolute()
        return str(tf)

    response_handlers: ClassVar[dict[str, Any]] = {"text/html": None, "application/json": None}
    default_accept_mimetype = "text/html"

    # Request parsing
    request_read_args: ClassVar[dict[str, Any]] = {}
    request_view_args: ClassVar[dict[str, Any]] = {}


class RequestUIResourceConfig(UIResourceConfig):
    """Config for request detail page."""

    url_prefix = "/requests"
    api_service = "requests"
    blueprint_name = "oarepo_requests_ui"
    template_folder = "templates"
    templates: ClassVar[dict[str, Any]] = {
        "detail": "RequestDetail",
    }
    routes: ClassVar[dict[str, Any]] = {
        "detail": "/<pid_value>",
    }
    ui_serializer_class = "oarepo_requests.resources.ui.OARepoRequestsUIJSONSerializer"
    ui_links_item: ClassVar[dict[str, Any]] = {}
    components = (AllowedHtmlTagsComponent,)

    error_handlers: ClassVar[dict[type[Exception], Any]] = {
        PIDDeletedError: "tombstone",
        PIDDoesNotExistError: "not_found",
        PIDUnregistered: "not_found",
        KeyError: "not_found",
        PermissionDeniedError: "permission_denied",
    }

    request_view_args: ClassVar[dict[str, Any]] = {"pid_value": ma.fields.Str()}

    @property
    def ui_serializer(self) -> BaseSerializer:
        """Return the UI serializer for the request."""
        return obj_or_import_string(self.ui_serializer_class)()

    def custom_fields(self, **kwargs: Any) -> dict:
        """Get the custom fields for the request."""
        api_service = current_service_registry.get(self.api_service)

        ui: list[dict] = []
        ret = {
            "ui": ui,
        }

        # get the record class
        if not hasattr(api_service, "record_cls"):
            return ret
        record_class: type[Record] = api_service.record_cls
        if not record_class:
            return ret
        # try to get custom fields from the record
        for _fld_name, fld in sorted(inspect.getmembers(record_class)):
            """
            if isinstance(fld, InlinedCustomFields):
                prefix = ""
            elif isinstance(fld, CustomFields):
                prefix = fld.key + "."
            else:
                continue
            """

            ui_config = _get_custom_fields_ui_config(fld.config_key, **kwargs)
            if not ui_config:
                continue

            for section in ui_config:  # TODO: ...
                ui.append(  # noqa PERF401
                    {
                        **section,
                        "fields": [
                            {
                                **field,
                                "field": field["field"],  # TODO: original: "field": prefix + field["field"]
                            }
                            for field in section.get("fields", [])
                        ],
                    }
                )
        return ret
