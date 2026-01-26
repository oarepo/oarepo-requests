#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations


def test_requests_field(
    logged_client,
    users,
    urls,
    draft_factory,
    create_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    resp_request_create = create_request_on_draft(creator.identity, draft1_id, "publish_draft")
    creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft")
    expanded_record = receiver_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true")

    assert "requests" not in record.json.get("expanded", {})
    assert "requests" in expanded_record.json["expanded"]


def test_autoaccept_receiver(
    logged_client,
    users,
    urls,
    create_request_on_record,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    resp_request_submit = create_request_on_record(creator.identity, record1["id"], "edit_published_record")
    request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}?expand=true").json
    assert request["expanded"]["receiver"] == {"auto_approve": "true"}


def test_multiple_recipients(
    logged_client,
    users,
    urls,
    create_request_on_draft,
    draft_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    recipient1_id = str(users[0].id)
    recipient2_id = str(users[1].id)

    record1 = draft_factory(creator.identity, custom_workflow="multiple_recipients")
    resp_request_submit = create_request_on_draft(creator.identity, record1["id"], "publish_draft")
    request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}?expand=true").json
    assert request["expanded"]["receiver"] == {
        "user": {
            recipient1_id: {
                "active": True,
                "blocked_at": None,
                "confirmed_at": None,
                "email": "user1@example.org",
                "id": recipient1_id,
                "is_current_user": True,
                "links": {
                    "avatar": f"https://127.0.0.1:5000/api/users/{recipient1_id}/avatar.svg",
                    "records_html": f"https://127.0.0.1:5000/search/records?q=parent.access.owned_by.user:{recipient1_id}",
                    "self": f"https://127.0.0.1:5000/api/users/{recipient1_id}",
                },
                "profile": {"affiliations": "CERN", "full_name": ""},
                "username": None,
                "verified_at": None,
            },
            recipient2_id: {
                "active": None,
                "blocked_at": None,
                "confirmed_at": None,
                "email": "",
                "id": recipient2_id,
                "is_current_user": False,
                "links": {
                    "avatar": f"https://127.0.0.1:5000/api/users/{recipient2_id}/avatar.svg",
                    "records_html": f"https://127.0.0.1:5000/search/records?q=parent.access.owned_by.user:{recipient2_id}",
                    "self": f"https://127.0.0.1:5000/api/users/{recipient2_id}",
                },
                "profile": {"affiliations": "CERN", "full_name": ""},
                "username": "beetlesmasher",
                "verified_at": None,
            },
        }
    }


def test_draft_topic(
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    draft1 = draft_factory(creator.identity)
    request = submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
    expanded_record = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{request['id']}?expand=true").json
    assert "topic" in expanded_record["expanded"]
