import pytest
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.permissions.presets import CreatorsFromWorkflowPermissionPolicy
from tests.test_requests.utils import link_api2testclient


@unit_of_work()
def change_workflow(identity, service, record, function, uow=None):
    function(identity, record, "with_approve")
    uow.register(RecordCommitOp(record, indexer=service.indexer))
    uow.register(ParentRecordCommitOp(record.parent))


@pytest.fixture()
def scenario_permissions():
    return CreatorsFromWorkflowPermissionPolicy


@pytest.fixture()
def requests_service_config():
    from invenio_requests.services.requests.config import RequestsServiceConfig

    return RequestsServiceConfig


@pytest.fixture
def patch_requests_permissions(
    requests_service_config,
    scenario_permissions,
):
    setattr(requests_service_config, "permission_policy_cls", scenario_permissions)


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
