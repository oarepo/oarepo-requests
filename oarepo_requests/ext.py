from oarepo_requests.resources.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.resource import OARepoRequestsResource
from oarepo_requests.services.config import OARepoRequestsServiceConfig
from oarepo_requests.services.service import OARepoRequestsService


class OARepoRequests:
    def __init__(self, app=None):
        """Extension initialization."""
        self.requests_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_services(app)
        self.init_resources(app)
        app.extensions["oarepo-requests"] = self

    @property
    def entity_resolvers(self):
        return self.app.config["ENTITY_REFERENCE_UI_RESOLVERS"]

    # copied from invenio_requests for now
    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            requests = OARepoRequestsServiceConfig.build(app)
            # request_events = RequestEventsServiceConfig.build(app)

        return ServiceConfigs

    def init_services(self, app):
        service_configs = self.service_configs(app)
        """Initialize the service and resource for Requests."""
        self.requests_service = OARepoRequestsService(config=service_configs.requests)
        # self.request_events_service = RequestEventsService(
        #    config=service_configs.request_events,
        # )

    def init_resources(self, app):
        """Init resources."""
        self.requests_resource = OARepoRequestsResource(
            service=self.requests_service,
            config=OARepoRequestsResourceConfig.build(app),
        )
