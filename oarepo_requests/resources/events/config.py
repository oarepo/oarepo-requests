"""Resource configuration for events and comments."""

from flask_resources import ResponseHandler
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources.events.config import RequestCommentsResourceConfig

from oarepo_requests.resources.ui import OARepoRequestEventsUIJSONSerializer


class OARepoRequestsCommentsResourceConfig(
    RequestCommentsResourceConfig, ConfiguratorMixin
):
    """Resource configuration for comments."""

    blueprint_name = "oarepo_request_events"
    url_prefix = "/requests"
    routes = {
        **RequestCommentsResourceConfig.routes,
        "list-extended": "/extended/<request_id>/comments",
        "item-extended": "/extended/<request_id>/comments/<comment_id>",
        "timeline-extended": "/extended/<request_id>/timeline",
    }

    @property
    def response_handlers(self) -> dict[str, ResponseHandler]:
        """Get response handlers.

        :return: Response handlers (dict of content-type -> handler)
        """
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestEventsUIJSONSerializer()
            ),
            **super().response_handlers,
        }
