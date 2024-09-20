from oarepo_requests.resources.record.types.config import (
    RecordRequestTypesResourceConfig,
)


class DraftRequestTypesResourceConfig(RecordRequestTypesResourceConfig):

    routes = {
        **RecordRequestTypesResourceConfig.routes,
        "list-applicable-requests-draft": "/<pid_value>/draft/requests/applicable",
    }
