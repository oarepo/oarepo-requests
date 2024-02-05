from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """"""

    blueprint_name = "draft-record-requests"
    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-drafts": "/<pid_value>/draft/requests",
    }
