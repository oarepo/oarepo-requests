from __future__ import annotations

from typing import Any, TYPE_CHECKING

import jsonpatch

from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import UnitOfWork
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from invenio_requests import current_events_service
from oarepo_runtime.datastreams.utils import get_record_service_for_record
import json

from oarepo_requests.models import RecordSnapshot
from oarepo_requests.types.events.record_snapshot import RecordSnapshotEventType
from invenio_db import db
from invenio_records_resources.services.uow import unit_of_work

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_requests.customizations import RequestType
    from invenio_requests.customizations.actions import RequestAction
    from sqlalchemy_utils.types import UUIDType


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
        
        # When request is accepted, then identity passed in this function is the identity of the receiver
        # which will cause PermissionDenied in read/read_draft
        # And check it just in case
        if identity.id != self.request.created_by.resolve().id:
            return super_apply 

        if not topic.is_draft:
            ret = service.read(identity, topic.pid.pid_value)
        else:
            ret = service.read_draft(identity, topic.pid.pid_value)

        create_snapshot_and_possible_event(topic, ret, self.request.id)

        return super_apply

@unit_of_work()
def create_snapshot_and_possible_event(topic: Record, record_item: Any, request_id: UUIDType, uow=None) -> None:
    """Creates new snapshot of a record and create possible event with old version, new version and difference between versions.
    
    :param Record topic: New topic to take snapshot of
    :param UUIDType request_id: Request id for given topic
    :param Any record_item: Record item with metadata, could be retrieved with service.read/read_draft(identity, topic.pid.pid_value), where service = get_record_service_for_record(topic)
    :param UnitOfWork uow: Unit of work to use (invenio)
    """
    RecordSnapshot.create(record_uuid=topic.id, request_id=request_id, json=record_item.to_dict()['metadata'])
    db.session.commit()

    # go through table, filter latest two
    # if two -> create event
    results = (db.session.query(RecordSnapshot)
                .filter_by(record_uuid=topic.id)
                .order_by(RecordSnapshot.created.desc())
                .limit(2)
                .all())


    if len(results) == 2:
        old_version = results[1].json
        new_version = record_item.to_dict()['metadata']
        diff = jsonpatch.JsonPatch.from_diff(old_version, new_version).patch
        # TODO if diff patch is replace or delelte add also previous value 
        data = {
            'payload': {
                'old_version': json.dumps(old_version),
                'new_version': json.dumps(new_version),
                'diff': json.dumps(diff)
            }
        }

        current_events_service.create(
            system_identity,
            request_id,
            data,
            event_type=RecordSnapshotEventType,
            uow=uow,
        )
