"""Components for request type and request expansion in record responses.

This module provides service components that handle the expansion of request-related
information when records are retrieved. The components are used to:

1. Expand request types available for a record (RequestTypesComponent)
2. Expand existing requests associated with a record (RequestsComponent)

Both components work with the 'expand' parameter in record retrieval operations
and add their data under the 'expanded' section of the response.
"""

#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_runtime.services.results import ResultComponent

from oarepo_requests.services.results import serialize_request_types
from oarepo_requests.utils import allowed_request_types_for_record, search_requests

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record


class RequestTypesComponent(ResultComponent):
    """Component for expanding request types."""

    def update_data(self, identity: Identity, record: Record, projection: dict, expand: bool) -> None:
        """Expand request types if requested."""
        if not expand:
            return
        allowed_request_types = allowed_request_types_for_record(identity, record)
        request_types_list = serialize_request_types(allowed_request_types, identity, record)
        projection["expanded"]["request_types"] = request_types_list


class RequestsComponent(ResultComponent):
    """Component for expanding requests on a record."""

    def update_data(self, identity: Identity, record: Record, projection: dict, expand: bool) -> None:
        """Expand requests if requested."""
        if not expand:
            return
        try:
            requests = list(search_requests(identity, record))
        except PermissionDeniedError:
            requests = []
        projection["expanded"]["requests"] = requests
