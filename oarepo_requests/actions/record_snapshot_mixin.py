from __future__ import annotations

from typing import Any, TYPE_CHECKING


from oarepo_runtime.datastreams.utils import get_record_service_for_record
from oarepo_requests.snapshots import create_snapshot_and_possible_event
from flask_principal import PermissionDenied
from contextlib import suppress

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations import RequestType
    from invenio_requests.customizations.actions import RequestAction
    from invenio_records_resources.services.uow import UnitOfWork


class RecordSnapshotMixin:
    def apply(
            self: RequestAction,
            identity: Identity,
            request_type: RequestType,
            topic: Record,
            uow: UnitOfWork,
            *args: Any,
            **kwargs: Any,
    ) -> Record:
        """Take snapshot of the record."""
        super_apply = super().apply(identity, request_type, topic, uow, *args, **kwargs)

        service = get_record_service_for_record(topic)
        
        with suppress(PermissionDenied):
            if not topic.is_draft:
                ret = service.read(identity, topic.pid.pid_value)
            else:
                ret = service.read_draft(identity, topic.pid.pid_value)

            create_snapshot_and_possible_event(topic, ret.to_dict()['metadata'], self.request.id)

        return super_apply    

