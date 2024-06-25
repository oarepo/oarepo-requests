from oarepo_requests.ui.config import RequestUIResourceConfig
from oarepo_requests.ui.resource import RequestUIResource


def create_blueprint(app):
    """Register blueprint for this resource."""
    return RequestUIResource(RequestUIResourceConfig()).as_blueprint()
