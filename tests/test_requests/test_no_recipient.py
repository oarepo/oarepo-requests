#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
def test_no_recipient(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    assert creator.id == '1'

    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="with_ct")

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json={
            "request_type": "approve_draft",
            "topic": {"thesis_draft": draft1.json["id"]},
        }
    )
    assert resp_request_create.status_code == 201
    assert resp_request_create.json['receiver'] is None
    assert resp_request_create.json['links']['receiver'] == {}
