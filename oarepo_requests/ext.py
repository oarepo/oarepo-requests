from invenio_requests.proxies import current_requests_service

from oarepo_requests.resources.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.resource import OARepoRequestsResource
from oarepo_requests.services.create import CreateRequestsService


class OARepoRequests:
    def __init__(self, app=None):
        """Extension initialization."""
        self.requests_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_resources()
        app.extensions["oarepo-requests"] = self

    def init_resources(self):
        """Init resources."""
        self.service = CreateRequestsService(current_requests_service)
        self.requests_resource = OARepoRequestsResource(
            service=self.service,
            config=OARepoRequestsResourceConfig(),
        )
