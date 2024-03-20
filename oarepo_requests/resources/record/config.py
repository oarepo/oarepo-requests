import marshmallow as ma
from invenio_records_resources.resources import RecordResourceConfig


class RecordRequestsResourceConfig:
    routes = {
        "list": "/<pid_value>/requests",
        "type": "/<pid_value>/requests/<request_type>",
    }
    request_view_args = RecordResourceConfig.request_view_args | {
        "request_type": ma.fields.Str()
    }
    """
    @property
    def response_handlers(self):
        return {
            **RequestsResourceConfig.routes,
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                OARepoRequestsUIJSONSerializer()
            ),
            **super().response_handlers,
        }
    """
