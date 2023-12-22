from oarepo_requests.resources.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.resource import OARepoRequestsResource


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
        self.requests_resource = OARepoRequestsResource(
            config=OARepoRequestsResourceConfig(),
        )