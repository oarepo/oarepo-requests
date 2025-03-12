from invenio_records_resources.services.records.components import ServiceComponent
from oarepo_requests.types.record_snapshot_mixin import create_snapshot_and_possible_event
from oarepo_runtime.datastreams.utils import get_record_service_for_record
from invenio_requests.records.models import RequestMetadata
from invenio_db import db

class RecordSnapshotComponent(ServiceComponent):

    def update(self, identity, *, record, **kwargs):
        """Update handler."""

        # get all requests with record id
        requests = [result for result in db.session.query(RequestMetadata).all() 
            if 'topic' in result.json and any(value == record['id'] for value in result.json['topic'].values())]
        
        # sort to get the latest one
        sorted_requests = sorted(requests, key=lambda x: x.updated)
        
        if sorted_requests:
            service = get_record_service_for_record(record)
            if record.is_draft:
                record_item = service.read_draft(identity, record.pid.pid_value)
            else:
                record_item = service.read(identity, record.pid.pid_value)
            
            create_snapshot_and_possible_event(record, record_item, sorted_requests[0].id)

    def update_draft(self, identity, *, record, **kwargs):

        # get all requests with record id
        requests = [result for result in db.session.query(RequestMetadata).all() 
            if 'topic' in result.json and any(value == record['id'] for value in result.json['topic'].values())]
        
        # sort to get the latest one
        sorted_requests = sorted(requests, key=lambda x: x.updated)

        if sorted_requests:
            service = get_record_service_for_record(record)
            if record.is_draft:
                record_item = service.read_draft(identity, record.pid.pid_value)
            else:
                record_item = service.read(identity, record.pid.pid_value)
            
            create_snapshot_and_possible_event(record, record_item, sorted_requests[0].id)
