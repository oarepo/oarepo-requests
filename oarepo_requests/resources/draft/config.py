"""Configuration of the draft record requests resource."""

from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """Configuration of the draft record requests resource."""

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests-draft": "/<pid_value>/draft/requests",
        "request-type-draft": "/<pid_value>/draft/requests/<request_type>",
    }
