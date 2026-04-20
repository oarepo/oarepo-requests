#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from oarepo_runtime.typing import record_from_result
from oarepo_workflows.errors import RequestTypeNotInWorkflowError

from oarepo_requests.errors import ReceiverNonReferencableError


def test_open_request_already_exists_error(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """Creating a duplicate request on the same topic returns 400 with descriptive message."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/publish_draft")
    assert resp.status_code == 201

    resp_duplicate = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/publish_draft")
    assert resp_duplicate.status_code == 400
    assert "already an open request" in resp_duplicate.json["message"]
    assert "Publish draft" in resp_duplicate.json["message"]


def test_unknown_request_type_error(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """Creating a request with a non-existent type returns 400."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/nonexistent_type")
    assert resp.status_code == 400
    assert "Unknown request type" in resp.json["message"]


def test_request_type_not_in_workflow_error(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """Creating a request with a non-existent type returns 400."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/conditional_recipient_rt")
    assert resp.status_code == 400
    # error defined in workflows
    assert resp.json["message"] == RequestTypeNotInWorkflowError("conditional_recipient_rt", "default").description


# TODO: clean up test workflows (we don't have topic updating now)
def test_unresolved_requests_error_on_publish_accept(
    requests_model,
    logged_client,
    users,
    urls,
    draft_factory,
    link2testclient,
    search_clear,
):
    """Accepting a publish request while another open request exists returns 400."""
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    # Use "cascade_update" workflow which has both publish_draft and another_topic_updating
    draft = draft_factory(creator.identity, custom_workflow="cascade_update")
    draft_id = draft["id"]

    # Create and submit publish_draft
    publish_resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/publish_draft")
    assert publish_resp.status_code == 201
    submit_resp = creator_client.post(link2testclient(publish_resp.json["links"]["actions"]["submit"]))
    assert submit_resp.status_code == 200

    # Create and submit another_topic_updating (uses AnyUser requester, user2 receiver)
    another_resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/another_topic_updating")
    assert another_resp.status_code == 201
    submit_another = creator_client.post(link2testclient(another_resp.json["links"]["actions"]["submit"]))
    assert submit_another.status_code == 200

    # Get the accept action URL from the expanded draft view (as receiver)
    requests_model.Draft.index.refresh()
    draft_record = receiver_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true").json
    publish_request = next(
        r for r in draft_record["expanded"]["requests"] if r["type"] == "publish_draft" and r["is_open"]
    )
    assert "accept" in publish_request["links"]["actions"]

    # Try to accept publish_draft — should fail because another_topic_updating is still open
    resp = receiver_client.post(link2testclient(publish_request["links"]["actions"]["accept"]))
    assert resp.status_code == 400
    body = resp.json
    assert "closed first" in body.get("message", "") or "Cannot" in body.get("message", "")


def test_version_already_exists_error_on_create(
    requests_model,
    logged_client,
    users,
    urls,
    record_factory,
    submit_request_on_record,
    search_clear,
):
    """Creating publish_new_version with a duplicate version tag returns 400."""
    from invenio_access.permissions import system_identity

    from oarepo_requests.proxies import current_requests_service

    creator = users[0]
    creator_client = logged_client(creator)
    record_service = requests_model.proxies.current_service
    record = record_factory(creator.identity, additional_data={"metadata": {"version": "1.0"}})
    record_id = record["id"]

    # Create a new version (auto-approved)
    topic = record_from_result(record_service.read(system_identity, record_id))
    nv_request = current_requests_service.create(
        identity=creator.identity,
        data={},
        request_type="new_version",
        topic=topic,
    )
    resp = current_requests_service.execute_action(creator.identity, nv_request["id"], "submit", expand=True)
    requests_model.Draft.index.refresh()
    requests_model.Record.index.refresh()
    new_draft_id = resp.to_dict()["expanded"]["payload"]["created_topic"]["id"]["id"]
    resp = creator_client.post(
        f"{urls['BASE_URL_REQUESTS']}record:{new_draft_id}/publish_new_version",
        json={"payload": {"version": "1.0"}},
    )
    assert resp.status_code == 400
    body = resp.json
    assert "version" in body.get("message", "").lower() or "request_payload_errors" in body


def test_create_request_failed_on_validation(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/publish_draft", json={"blabla": "lala"})
    assert resp.status_code == 400

    body = resp.json
    assert "status" in body
    assert body["status"] == 400
    assert "message" in body


def test_receiver_not_referencable_error(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """Creating a request with empty recipients fails when receiver_can_be_none=False."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity, custom_workflow="with_approve")
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}record:{draft_id}/generic")
    assert resp.status_code == 400
    assert (
        ReceiverNonReferencableError(
            "generic", record_from_result(current_rdm_records_service.read_draft(system_identity, draft_id))
        ).description
        in resp.json["message"]
    )
