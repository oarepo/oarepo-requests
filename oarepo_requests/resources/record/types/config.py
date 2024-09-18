import marshmallow as ma
from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer, OARepoRequestTypesUIJSONSerializer


class ApplicableRecordRequestsResourceConfig:
    routes = {
        "list-applicable-requests": "/<pid_value>/requests/applicable",
    }

    @property
    def response_handlers(self):
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestTypesUIJSONSerializer()
            ),
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        }
