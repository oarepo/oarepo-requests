from oarepo_ui.resources.config import RecordsUIResourceConfig
from oarepo_ui.resources.resource import RecordsUIResource

class RequestUIResourceConfig(RecordsUIResourceConfig):
    url_prefix = "/requests"
    blueprint_name = "oarepo_requests_ui"
    template_folder = "templates"
    templates = {
        "detail": "RequestDetail",
    }
    api_service = "requests"
    ui_serializer_class = "oarepo_requests.resources.ui.OARepoRequestsUIJSONSerializer"


class RequestUIResource(RecordsUIResource):
    pass


def create_blueprint(app):
    """Register blueprint for this resource."""
    return RequestUIResource(RequestUIResourceConfig()).as_blueprint()
