from flask_resources import ResponseHandler
from invenio_records_resources.resources.records.config import RecordResourceConfig
from invenio_requests.resources.requests.config import RequestsResourceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin

from .ui import OARepoRequestsUIJSONSerializer


class RecordRequestsResourceConfig(RecordResourceConfig):
    """"""

    blueprint_name = "record-requests"
    routes = {"list": "/<pid_value>/requests"}

    @property
    def response_handlers(self):
        return {
            **RequestsResourceConfig.routes,
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestsUIJSONSerializer()
            ),
            **super().response_handlers,
        }


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """"""

    blueprint_name = "draft-record-requests"
    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-drafts": "/<pid_value>/draft/requests",
    }


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
