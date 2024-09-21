from invenio_base.utils import obj_or_import_string
from invenio_requests.proxies import current_events_service

from oarepo_requests.resources.events.config import OARepoRequestsCommentsResourceConfig
from oarepo_requests.resources.events.resource import OARepoRequestsCommentsResource
from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService


class OARepoRequests:
    def __init__(self, app=None):
        """Extension initialization."""
        self.requests_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["oarepo-requests"] = self

    @property
    def entity_reference_ui_resolvers(self):
        return self.app.config["ENTITY_REFERENCE_UI_RESOLVERS"]

    @property
    def ui_serialization_referenced_fields(self):
        return self.app.config["REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS"]

    def default_request_receiver(self, identity, request_type, record, creator, data):
        # TODO: if the topic is one of the workflow topics, use the workflow to determine the receiver
        # otherwise use the default receiver
        return obj_or_import_string(
            self.app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]
        )(
            identity=identity,
            request_type=request_type,
            record=record,
            creator=creator,
            data=data,
        )

    @property
    def allowed_receiver_ref_types(self):
        return self.app.config.get("REQUESTS_ALLOWED_RECEIVERS", [])

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

    from invenio_requests.customizations.actions import RequestAction

    def action_components(self, action: RequestAction):
        from . import config

        components = config.REQUESTS_ACTION_COMPONENTS
        if callable(components):
            return components(action)
        return [
            obj_or_import_string(component)
            for component in components[action.status_to]
        ]

    def init_config(self, app):
        """Initialize configuration."""

        from . import config

        app.config.setdefault("REQUESTS_ALLOWED_RECEIVERS", []).extend(
            config.REQUESTS_ALLOWED_RECEIVERS
        )
        app.config.setdefault("ENTITY_REFERENCE_UI_RESOLVERS", {}).update(
            config.ENTITY_REFERENCE_UI_RESOLVERS
        )
        app.config.setdefault("REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS", []).extend(
            config.REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS
        )
        app.config.setdefault("DEFAULT_WORKFLOW_EVENT_SUBMITTERS", {}).update(
            config.DEFAULT_WORKFLOW_EVENT_SUBMITTERS
        )

        app.config.setdefault("REQUESTS_REGISTERED_EVENT_TYPES", []).extend(
            config.REQUESTS_REGISTERED_EVENT_TYPES
        )


def api_finalize_app(app):
    """Finalize app."""
    finalize_app(app)


def finalize_app(app):
    """Finalize app."""
    from invenio_requests.proxies import current_event_type_registry

    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    rr_ext = app.extensions["invenio-records-resources"]
    # idx_ext = app.extensions["invenio-indexer"]
    ext = app.extensions["oarepo-requests"]

    # services
    rr_ext.registry.register(
        ext.requests_service,
        service_id=ext.requests_service.config.service_id,
    )

    # todo i have to do this cause there is bug in invenio-requests for events
    # but imo this is better than entrypoints
    for type in app.config["REQUESTS_REGISTERED_EVENT_TYPES"]:
        current_event_type_registry.register_type(type)
