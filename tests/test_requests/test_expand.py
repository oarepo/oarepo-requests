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

    record1 = draft_factory(creator.identity, custom_workflow="multiple_recipients")
    resp_request_submit = create_request_on_draft(creator.identity, record1["id"], "publish_draft")
    request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}?expand=true").json
    assert request["expanded"]["receiver"] == {
        "user": {
            "1": {
                "active": True,
                "blocked_at": None,
                "confirmed_at": None,
                "email": "user1@example.org",
                "id": "1",
                "is_current_user": True,
                "links": {
                    "avatar": "https://127.0.0.1:5000/api/users/1/avatar.svg",
                    "records_html": "https://127.0.0.1:5000/search/records?q=parent.access.owned_by.user:1",
                    "self": "https://127.0.0.1:5000/api/users/1",
                },
                "profile": {"affiliations": "CERN", "full_name": ""},
                "username": None,
                "verified_at": None,
            },
            "2": {
                "active": None,
                "blocked_at": None,
                "confirmed_at": None,
                "email": "",
                "id": "2",
                "is_current_user": False,
                "links": {
                    "avatar": "https://127.0.0.1:5000/api/users/2/avatar.svg",
                    "records_html": "https://127.0.0.1:5000/search/records?q=parent.access.owned_by.user:2",
                    "self": "https://127.0.0.1:5000/api/users/2",
                },
                "profile": {"affiliations": "CERN", "full_name": ""},
                "username": "beetlesmasher",
                "verified_at": None,
            },
        }
    }
