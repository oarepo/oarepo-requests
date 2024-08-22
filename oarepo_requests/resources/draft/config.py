from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests-draft": "/<pid_value>/draft/requests",
        "list-applicable-requests-draft": "/<pid_value>/draft/requests/applicable",
        "request-type-draft": "/<pid_value>/draft/requests/<request_type>",
    }
