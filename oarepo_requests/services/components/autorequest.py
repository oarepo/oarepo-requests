#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from typing import TYPE_CHECKING

from invenio_records_resources.services.records.components import ServiceComponent

from oarepo_requests.services.permissions.requester import create_autorequests

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_records_resources.records import Record


class AutorequestComponent(ServiceComponent):
    """Component for assigning request numbers to new requests."""

    def create(self, identity: Identity, data: dict | None = None, record: Record = None, **kwargs) -> None:
        """Create requests that should be created automatically on state change.

        For each of the WorkflowRequest definition in the workflow of the record,
        take the needs from the generators of possible creators. If any of those
        needs is an auto_request_need, create a request for it automatically.
        """
        create_autorequests(identity, record, self.uow, **kwargs)
