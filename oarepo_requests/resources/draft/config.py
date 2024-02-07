from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """"""

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-drafts": "/<pid_value>/draft/requests",
    }
