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

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp.status_code == 201

    resp_duplicate = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp_duplicate.status_code == 400
    assert "already an open request" in resp_duplicate.json["message"]
    assert "Publish draft" in resp_duplicate.json["message"]


def test_open_request_already_exists_after_submit(
    logged_client,
    users,
    urls,
    draft_factory,
    link2testclient,
    search_clear,
):
    """Creating a duplicate request after the first has been submitted still returns 400."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp.status_code == 201
    creator_client.post(link2testclient(resp.json["links"]["actions"]["submit"]))

    resp_duplicate = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp_duplicate.status_code == 400
    assert "already an open request" in resp_duplicate.json["message"]


def test_open_request_recreatable_after_decline(
    logged_client,
    users,
    urls,
    draft_factory,
    link2testclient,
    search_clear,
):
    """After declining a request, a new one can be created on the same topic."""
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp.status_code == 201
    creator_client.post(link2testclient(resp.json["links"]["actions"]["submit"]))

    record = receiver_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true").json
    receiver_client.post(
        link2testclient(record["expanded"]["requests"][0]["links"]["actions"]["decline"]),
    )

    resp_new = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft")
    assert resp_new.status_code == 201


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

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/nonexistent_type")
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

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/conditional_recipient_rt")
    assert resp.status_code == 400
    # error defined in workflows
    assert resp.json["message"] == RequestTypeNotInWorkflowError("conditional_recipient_rt", "default").description

# TODO: decide what to do with this once we are using invenio reviews
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
    publish_resp = creator_client.post(
        f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft"
    )
    assert publish_resp.status_code == 201
    submit_resp = creator_client.post(link2testclient(publish_resp.json["links"]["actions"]["submit"]))
    assert submit_resp.status_code == 200

    # Create and submit another_topic_updating (uses AnyUser requester, user2 receiver)
    another_resp = creator_client.post(
        f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/another_topic_updating"
    )
    assert another_resp.status_code == 201
    submit_another = creator_client.post(link2testclient(another_resp.json["links"]["actions"]["submit"]))
    assert submit_another.status_code == 200

    # Get the accept action URL from the expanded draft view (as receiver)
    requests_model.Draft.index.refresh()
    draft_record = receiver_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true").json
    publish_request = next(
        r for r in draft_record["expanded"]["requests"]
        if r["type"] == "publish_draft" and r["is_open"]
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

    # Create a published record with version "1.0"
    record = record_factory(creator.identity, additional_data={"metadata": {"version": "1.0"}})
    record_id = record["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    # Create a new version (auto-approved)
    topic = record_service.read(system_identity, record_id)._obj  # noqa: SLF001
    nv_request = current_requests_service.create(
        identity=creator.identity,
        data={},
        request_type="new_version",
        topic=topic,
    )
    current_requests_service.execute_action(creator.identity, nv_request["id"], "submit")
    requests_model.Draft.index.refresh()
    requests_model.Record.index.refresh()

    # Read the accepted request to get the new draft topic
    nv_result = current_requests_service.read(creator.identity, nv_request["id"]).to_dict()
    # The new version draft reference is in the topic (which changes to the new draft after accept)
    # or we can find it by searching user drafts
    new_draft_id = None
    all_drafts = creator_client.get(f"/user{urls['BASE_URL']}?allversions=true").json["hits"]["hits"]
    for d in all_drafts:
        if d["id"] != record_id and not d.get("is_published", True):
            new_draft_id = d["id"]
            break

    assert new_draft_id is not None, (
        f"Could not find new version draft. All user records: {[(d['id'], d.get('status'), d.get('is_published')) for d in all_drafts]}"
    )

    # Try to create publish_new_version with the same version "1.0"
    resp = creator_client.post(
        f"{urls['BASE_URL_REQUESTS']}requests_test:{new_draft_id}/publish_new_version",
        json={"payload": {"version": "1.0"}},
    )
    assert resp.status_code == 400
    body = resp.json
    assert "version" in body.get("message", "").lower() or "request_payload_errors" in body


# TODO: used when validation errors are thrown in main service create; out-of-pattern, consider if we want this
def test_custom_http_json_exception_body_format(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """CustomHTTPJSONException responses include status and message fields."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity)
    draft_id = draft["id"]

    resp = creator_client.post(f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/publish_draft", json={"blabla": "lala"})
    assert resp.status_code == 400

    body = resp.json
    assert "status" in body
    assert body["status"] == 400
    assert "message" in body
    assert "request_payload_errors" in body


def test_receiver_not_referencable_error(
    logged_client,
    users,
    urls,
    draft_factory,
    search_clear,
):
    """Creating a request with empty recipients succeeds when receiver_can_be_none=True."""
    creator = users[0]
    creator_client = logged_client(creator)

    draft = draft_factory(creator.identity, custom_workflow="with_approve")
    draft_id = draft["id"]

    resp = creator_client.post(
        f"{urls['BASE_URL_REQUESTS']}requests_test:{draft_id}/generic"
    )
    assert resp.status_code == 400
    assert ReceiverNonReferencableError("generic", current_rdm_records_service.read_draft(system_identity, draft_id)._record).description in resp.json["message"]
