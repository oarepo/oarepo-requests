from flask_resources import ResponseHandler
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_requests.resources import RequestsResourceConfig

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer


class OARepoRequestsResourceConfig(RequestsResourceConfig, ConfiguratorMixin):
    """"""

    blueprint_name = "oarepo-requests"
    url_prefix = "/requests"
    routes = {
        **RequestsResourceConfig.routes,
        "list": "/",
        "list-extended": "/extended",
        "item-extended": "/extended/<id>",
    }

    @property
    def response_handlers(self):
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestsUIJSONSerializer()
            ),
            **super().response_handlers,
        }
