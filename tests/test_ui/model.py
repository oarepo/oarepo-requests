from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent
from thesis.resources.records.ui import ThesisUIJSONSerializer

from oarepo_requests.components import AllowedRequestsComponent


class ModelUIResourceConfig(RecordsUIResourceConfig):
    api_service = (
        "thesis"  # must be something included in oarepo, as oarepo is used in tests
    )

    blueprint_name = "thesis"
    url_prefix = "/thesis/"
    ui_serializer_class = ThesisUIJSONSerializer
    templates = {
        **RecordsUIResourceConfig.templates,
        "detail": {"layout": "test_detail.html", "blocks": {}},
        "search": {
            "layout": "test_detail.html",
        },
        "edit": {"layout": "test_edit.html"},
    }

    components = [BabelComponent, PermissionsComponent, AllowedRequestsComponent]


class ModelUIResource(RecordsUIResource):
    pass
