import marshmallow as ma
from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer


class RecordRequestsResourceConfig:
    routes = {
        "list-requests": "/<pid_value>/requests",
        "list-applicable-requests": "/<pid_value>/requests/applicable",
        "request-type": "/<pid_value>/requests/<request_type>",
    }
    request_view_args = RecordResourceConfig.request_view_args | {
        "request_type": ma.fields.Str()
    }

    @property
    def response_handlers(self):
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestsUIJSONSerializer()
            ),
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        }
