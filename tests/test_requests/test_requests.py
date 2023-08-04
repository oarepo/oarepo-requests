import pytest
from invenio_access.permissions import system_identity
from sqlalchemy.orm.exc import NoResultFound

from invenio_pidstore.errors import PIDUnregistered, PIDDeletedError



def test_workflow(
    requests_service,
    record_service,
    example_topic_draft
):
    record_id = example_topic_draft["id"]

    resp1 = record_service.read_draft(system_identity, record_id)
    with pytest.raises(PIDUnregistered):
        record_service.read(system_identity, record_id)

    requests_service.execute_action(system_identity, resp1._obj.parent.publish_draft.id, "submit")

    with pytest.raises(NoResultFound):
        record_service.read_draft(system_identity, record_id)
    resp2 = record_service.read(system_identity, record_id)
    assert resp2._obj.parent.publish_draft is None

    requests_service.execute_action(system_identity, resp2._obj.parent.delete_record.id, "submit")

    with pytest.raises(PIDDeletedError):
        record_service.read_draft(system_identity, record_id)
    with pytest.raises(PIDDeletedError):
        record_service.read(system_identity, record_id)

def test_direct_publish_request_deleted(    requests_service,
    record_service,
    example_topic_draft):

    record_id = example_topic_draft["id"]
    resp = record_service.publish(system_identity, record_id)

    assert resp._obj.parent.publish_draft is None
