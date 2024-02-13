from invenio_records_resources.resources import RecordResourceConfig


class RecordRequestsResourceConfig(RecordResourceConfig):
    routes = {"list": "/<pid_value>/requests"}
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
