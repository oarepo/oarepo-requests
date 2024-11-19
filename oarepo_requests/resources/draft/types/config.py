"""Draft request types resource configuration."""

from oarepo_requests.resources.record.types.config import (
    RecordRequestTypesResourceConfig,
)


class DraftRequestTypesResourceConfig(RecordRequestTypesResourceConfig):
    """Draft request types resource configuration."""

    routes = {
        **RecordRequestTypesResourceConfig.routes,
        "list-applicable-requests-draft": "/<pid_value>/draft/requests/applicable",
    }
