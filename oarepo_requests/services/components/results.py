from __future__ import annotations

from flask_principal import Identity
from invenio_records_resources.records import Record
from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_runtime.services.results import ResultComponent

from oarepo_requests.services.results import serialize_request_types
from oarepo_requests.temp_utils import search_requests
from oarepo_requests.utils import allowed_request_types_for_record


class RequestTypesComponent(ResultComponent):
    """Component for expanding request types."""

    def update_data(
        self, identity: Identity, record: Record, projection: dict, expand: bool
    ) -> None:
        """Expand request types if requested."""
        if not expand:
            return
        allowed_request_types = allowed_request_types_for_record(identity, record)
        request_types_list = serialize_request_types(
            allowed_request_types, identity, record
        )
        projection["expanded"]["request_types"] = request_types_list


class RequestsComponent(ResultComponent):
    """Component for expanding requests on a record."""

    def update_data(
        self, identity: Identity, record: Record, projection: dict, expand: bool
    ) -> None:
        """Expand requests if requested."""
        if not expand:
            return
        try:
            requests = list(search_requests(identity, record))
        except PermissionDeniedError:
            requests = []
        projection["expanded"]["requests"] = requests
