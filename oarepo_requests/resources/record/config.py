from flask_resources import ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig
from invenio_requests.resources import RequestsResourceConfig

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer


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
