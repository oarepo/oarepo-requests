from oarepo_requests.resources.record.types.config import (
    ApplicableRecordRequestsResourceConfig,
)


class ApplicableDraftRequestsResourceConfig(ApplicableRecordRequestsResourceConfig):

    routes = {
        **ApplicableRecordRequestsResourceConfig.routes,
        "list-applicable-requests-draft": "/<pid_value>/draft/requests/applicable",
    }
