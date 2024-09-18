import pytest
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.services.permissions.workflow_policies import (
    CreatorsFromWorkflowRequestsPermissionPolicy,
)
from tests.test_requests.utils import link_api2testclient


@unit_of_work()
def change_workflow(identity, service, record, function, uow=None):
    function(identity, record, "with_approve")
    uow.register(RecordCommitOp(record, indexer=service.indexer))
    uow.register(ParentRecordCommitOp(record.parent))


@pytest.fixture()
def scenario_permissions():
    return CreatorsFromWorkflowRequestsPermissionPolicy


@pytest.fixture()
def requests_service_config():
    from invenio_requests.services.requests.config import RequestsServiceConfig

    return RequestsServiceConfig


@pytest.fixture()
def events_service_config():
    from invenio_requests.services.events.config import RequestEventsServiceConfig

    return RequestEventsServiceConfig


@pytest.fixture
def patch_requests_permissions(
    requests_service_config,
    events_service_config,
    scenario_permissions,
):
    setattr(requests_service_config, "permission_policy_cls", scenario_permissions)
    setattr(events_service_config, "permission_policy_cls", scenario_permissions)


@pytest.fixture()
def status_changing_publish_request_data_function():
    def ret_data(record_id):
        return {
            "request_type": "publish_draft",
            "topic": {"thesis_draft": record_id},
        }

    return ret_data


def test_publish_with_workflows(
    vocab_cf,
    logged_client,
    users,
    urls,
    status_changing_publish_request_data_function,
    create_draft_via_resource,
    patch_requests_permissions,
    record_service,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    # test record owner can create publish request
    create_non_owner = receiver_client.post(
        urls["BASE_URL_REQUESTS"],
        json=status_changing_publish_request_data_function(draft1.json["id"]),
    )
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=status_changing_publish_request_data_function(draft1.json["id"]),
    )
    assert create_non_owner.status_code == 403
    assert resp_request_create.status_code == 201

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    assert resp_request_submit.status_code == 200

    # test state of the record is changed to published
    draft_with_submitted_request = record_service.read_draft(
        creator.identity, draft1.json["id"]
    )._record
    assert draft_with_submitted_request["state"] == "publishing"

    record_creator = creator_client.get(
        f'{urls["BASE_URL"]}{draft1.json["id"]}/draft?expand=true'
    ).json
    record_receiver = receiver_client.get(
        f'{urls["BASE_URL"]}{draft1.json["id"]}/draft?expand=true'
    ).json

    assert "accept" not in record_creator["expanded"]["requests"][0]["links"]["actions"]
    assert {"accept", "decline"} == record_receiver["expanded"]["requests"][0]["links"][
        "actions"
    ].keys()

    accept = receiver_client.post(
        link_api2testclient(
            record_receiver["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    assert accept.status_code == 200
    published_record = record_service.read(creator.identity, draft1.json["id"])._record
    assert published_record["state"] == "published"


def test_autorequest(
    db,
    vocab_cf,
    logged_client,
    users,
    urls,
    patch_requests_permissions,
    record_service,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="with_approve")
    record_id = draft1.json["id"]

    approve_request_data = {
        "request_type": "approve_draft",
        "topic": {"thesis_draft": str(record_id)},
    }
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=approve_request_data,
    )
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    approving_record = record_service.read_draft(creator.identity, record_id)._record
    assert resp_request_submit.status_code == 200
    assert approving_record["state"] == "approving"
    record_receiver = receiver_client.get(
        f'{urls["BASE_URL"]}{record_id}/draft?expand=true'
    ).json
    accept = receiver_client.post(
        link_api2testclient(
            record_receiver["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    assert accept.status_code == 200

    # the publish request should be created automatically
    publishing_record = record_service.read_draft(creator.identity, record_id)._record
    assert publishing_record["state"] == "publishing"


def test_if_no_new_version_draft(
    vocab_cf,
    patch_requests_permissions,
    logged_client,
    users,
    urls,
    new_version_data_function,
    edit_record_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    id_ = record["id"]
    id2_ = record2["id"]

    record = creator_client.get(
        f"{urls['BASE_URL']}{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "new_version" in {r["type_id"] for r in requests}

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(id_),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "new_version" not in {
        r["type_id"] for r in requests
    }  # new version created, requests should not be available again

    record = creator_client.get(  # try if edit is still allowed?; does it make sense edit request while also creating new version?
        f"{urls['BASE_URL']}{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=edit_record_data_function(id2_),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "new_version" in {
        r["type_id"] for r in requests
    }  # new version created, requests should not be available again


def test_if_no_edit_draft(
    vocab_cf,
    patch_requests_permissions,
    logged_client,
    users,
    urls,
    new_version_data_function,
    edit_record_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    id_ = record["id"]
    id2_ = record2["id"]

    record = creator_client.get(
        f"{urls['BASE_URL']}{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "edit_published_record" in {r["type_id"] for r in requests}

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=edit_record_data_function(id_),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "edit_published_record" not in {
        r["type_id"] for r in requests
    }  # new version created, requests should not be available again

    record = creator_client.get(  # try if edit_published_record is still allowed?; does it make sense edit request while also creating new version?
        f"{urls['BASE_URL']}{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(id2_),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "edit_published_record" in {
        r["type_id"] for r in requests
    }  # new version created, should edit be allowed with new version?


def test_workflow_events(
    logged_client,
    users,
    urls,
    patch_requests_permissions,
    record_service,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    events_resource_data,
    create_draft_via_resource,
    search_clear,
):
    user1 = users[0]
    user2 = users[1]

    user1_client = logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = create_draft_via_resource(user1_client, custom_workflow="with_approve")
    record_id = draft1.json["id"]

    approve_request_data = {
        "request_type": "approve_draft",
        "topic": {"thesis_draft": str(record_id)},
    }
    resp_request_create = user1_client.post(
        urls["BASE_URL_REQUESTS"],
        json=approve_request_data,
    )
    resp_request_submit = user1_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    read_from_record = user1_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true",
    )
    comments_link = link_api2testclient(
        read_from_record.json["expanded"]["requests"][0]["links"]["comments"]
    )
    comment_from1 = user1_client.post(
        comments_link,
        json=events_resource_data,
    )
    comment_from2 = user2_client.post(
        comments_link,
        json=events_resource_data,
    )

    assert comment_from1.status_code == 201
    assert comment_from2.status_code == 201

    record_receiver = user2_client.get(
        f'{urls["BASE_URL"]}{record_id}/draft?expand=true'
    ).json
    accept = user2_client.post(
        link_api2testclient(
            record_receiver["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    assert accept.status_code == 200
    publishing_record = record_service.read_draft(user1.identity, record_id)._record
    assert publishing_record["state"] == "publishing"

    read_from_record = user2_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true",
    )
    publish_request = [
        request
        for request in read_from_record.json["expanded"]["requests"]
        if request["type"] == "publish_draft"
    ][0]
    comments_link = link_api2testclient(publish_request["links"]["comments"])

    comment_from1 = user1_client.post(
        comments_link,
        json=events_resource_data,
    )
    comment_from2 = user2_client.post(
        comments_link,
        json=events_resource_data,
    )
    assert comment_from1.status_code == 201  # 1 is receiver for the publish request
    assert comment_from2.status_code == 403
