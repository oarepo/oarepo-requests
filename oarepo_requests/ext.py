from invenio_base.utils import obj_or_import_string

from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService

from oarepo_requests.resources.events.resource import OARepoRequestsCommentsResource
from oarepo_requests.resources.events.config import OARepoRequestsCommentsResourceConfig

from invenio_requests.proxies import current_events_service


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
    def entity_reference_ui_resolvers(self):
        return self.app.config["ENTITY_REFERENCE_UI_RESOLVERS"]

    def default_request_receiver(self, request_type_id):
        """
        returns function that returns default request receiver
        def receiver_getter(identity, request_type, topic, creator):
            return <dark magic here>
        """
        return obj_or_import_string(
            self.app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]
        )[request_type_id]

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

    def init_resources(self, app):
        """Init resources."""
        self.requests_resource = OARepoRequestsResource(
            oarepo_requests_service=self.requests_service,
            config=OARepoRequestsResourceConfig.build(app),
        )
        self.request_events_resource = OARepoRequestsCommentsResource(
            service=current_events_service,
            config=OARepoRequestsCommentsResourceConfig.build(app),
        )
