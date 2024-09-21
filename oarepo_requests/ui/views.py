from oarepo_ui.resources.resource import FormConfigResource

from oarepo_requests.ui.config import (
    RequestsFormConfigResourceConfig,
    RequestUIResourceConfig,
)
from oarepo_requests.ui.resource import RequestUIResource


def create_blueprint(app):
    """Register blueprint for this resource."""
    return RequestUIResource(RequestUIResourceConfig()).as_blueprint()


def create_requests_form_config_blueprint(app):
    """Register blueprint for form config resource"""
    return FormConfigResource(RequestsFormConfigResourceConfig()).as_blueprint()
