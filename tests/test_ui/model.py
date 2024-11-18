from flask import g
from flask_principal import PermissionDenied
from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent
from thesis.resources.records.ui import ThesisUIJSONSerializer
from werkzeug.exceptions import Forbidden


class ModelUIResourceConfig(RecordsUIResourceConfig):
    api_service = (
        "thesis"  # must be something included in oarepo, as oarepo is used in tests
    )

    blueprint_name = "thesis"
    url_prefix = "/thesis/"
    ui_serializer_class = ThesisUIJSONSerializer

    templates = {
        **RecordsUIResourceConfig.templates,
        "detail": "TestDetail",
        "search": "TestDetail",
        "edit": "TestEdit",
    }

    components = [BabelComponent, PermissionsComponent]


class ModelUIResource(RecordsUIResource):
    def _get_record(self, resource_requestctx, allow_draft=False):
        try:
            if allow_draft:
                read_method = (
                    getattr(self.api_service, "read_draft") or self.api_service.read
                )
            else:
                read_method = self.api_service.read

            return read_method(
                g.identity, resource_requestctx.view_args["pid_value"], expand=True
            )
        except PermissionDenied as e:
            raise Forbidden() from e
