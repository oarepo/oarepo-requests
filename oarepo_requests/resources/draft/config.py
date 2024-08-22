from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests": "/<pid_value>/draft/requests",
        "list-applicable-requests": "/<pid_value>/draft/requests/applicable",
        "request-type": "/<pid_value>/draft/requests/<request_type>",
    }
