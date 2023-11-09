import pytest
from invenio_pidstore.errors import PIDDeletedError, PIDUnregistered
from sqlalchemy.orm.exc import NoResultFound
from invenio_records_resources.services.errors import PermissionDeniedError


def test_workflow(
    requests_service,
    record_service,
    example_topic_draft,
    identity_simple,
):
    record_id = example_topic_draft["id"]

    resp1 = record_service.read_draft(identity_simple, record_id)
    with pytest.raises(PIDUnregistered):
        record_service.read(identity_simple, record_id)

    requests_service.execute_action(
        identity_simple, resp1._obj.parent.publish_draft.id, "submit"
    )

    with pytest.raises(NoResultFound):
        record_service.read_draft(identity_simple, record_id)
    resp2 = record_service.read(identity_simple, record_id)
    assert resp2._obj.parent.publish_draft is None

    requests_service.execute_action(
        identity_simple, resp2._obj.parent.delete_record.id, "submit"
    )

    with pytest.raises(PIDDeletedError):
        record_service.read_draft(identity_simple, record_id)
    with pytest.raises(PIDDeletedError):
        record_service.read(identity_simple, record_id)


def test_direct_publish_request_deleted(
    requests_service, record_service, example_topic_draft, identity_simple
):
    record_id = example_topic_draft["id"]
    resp = record_service.publish(identity_simple, record_id)

    assert resp._obj.parent.publish_draft is None


def test_parent_dump(
    requests_service, record_service, example_topic_draft, identity_simple
):
    record_id = example_topic_draft["id"]

    resp1 = record_service.read_draft(identity_simple, record_id)

    assert "parent" in resp1.data
    assert "publish_draft" in resp1.data["parent"]
    assert "delete_record" not in resp1.data["parent"]

    requests_service.execute_action(
        identity_simple, resp1.data["parent"]["publish_draft"]["id"], "submit"
    )
    resp2 = record_service.read(identity_simple, record_id)

    assert "parent" in resp2.data
    assert "publish_draft" not in resp2.data["parent"]
    assert "delete_record" in resp2.data["parent"]

    requests_service.execute_action(
        identity_simple, resp2.data["parent"]["delete_record"]["id"], "submit"
    )

    with pytest.raises(PIDDeletedError):
        record_service.read_draft(identity_simple, record_id)
    with pytest.raises(PIDDeletedError):
        record_service.read(identity_simple, record_id)

def test_receiver_permissions_user(request_with_receiver_user, requests_service, identity_creator, identity_receiver):
    request_id = request_with_receiver_user.id

    with pytest.raises(PermissionDeniedError):
        receiver_submit = requests_service.execute_action(identity=identity_receiver, id_=request_id, action="submit")
    creator_submit = requests_service.execute_action(identity=identity_creator, id_=request_id, action="submit")
    assert creator_submit.data["status"] == "submitted"

    with pytest.raises(PermissionDeniedError):
        creator_accept = requests_service.execute_action(identity=identity_creator, id_=request_id, action="accept")
    receiver_accept = requests_service.execute_action(identity=identity_receiver, id_=request_id, action="accept")
    assert receiver_accept.data["status"] == "accepted"

