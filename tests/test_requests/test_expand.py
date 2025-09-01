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
    resp_request_submit = creator_client.post(
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
