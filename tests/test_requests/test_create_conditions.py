#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations


def test_can_create(
    logged_client,
    users,
    urls,
    draft_factory,
    link2testclient,
    location,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft2 = draft_factory(creator.identity)

    draft1_id = draft1["id"]
    draft2_id = draft2["id"]

    resp_request_create = creator_client.post(
        f"{urls['BASE_URL']}/{draft1_id}/draft/requests/publish_draft"
    ).json

    resp = creator_client.post(  # create request after create
        f"{urls['BASE_URL']}/{draft1_id}/draft/requests/publish_draft"
    )
    assert resp.status_code == 400
    assert "There is already an open request of Publish draft" in resp.json["message"]

    creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )

    resp = creator_client.post(  # create request after submit
        f"{urls['BASE_URL']}/{draft1_id}/draft/requests/publish_draft"
    )
    assert resp.status_code == 400
    assert "There is already an open request of Publish draft" in resp.json["message"]

    # should still be creatable for draft2
    create_for_request_draft2 = creator_client.post(
        f"{urls['BASE_URL']}/{draft2_id}/draft/requests/publish_draft"
    )
    assert create_for_request_draft2.status_code == 201

    # try declining the request for draft2, we should be able to create again then
    creator_client.post(
        link2testclient(create_for_request_draft2.json["links"]["actions"]["submit"]),
    )

    create_for_request_draft2 = creator_client.post(
        f"{urls['BASE_URL']}/{draft2_id}/draft/requests/publish_draft"
    )
    assert create_for_request_draft2.status_code == 400
    assert (
        "There is already an open request of Publish draft"
        in create_for_request_draft2.json["message"]
    )

    record = receiver_client.get(
        f"{urls['BASE_URL']}/{draft2_id}/draft?expand=true"
    ).json
    decline = receiver_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )

    resp_request_create_again = creator_client.post(
        f"{urls['BASE_URL']}/{draft2_id}/draft/requests/publish_draft"
    )
    assert resp_request_create_again.status_code == 201


def test_can_possibly_create(
    logged_client,
    users,
    urls,
    draft_factory,
    link2testclient,
    location,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    record_resp_no_request = creator_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true"
    ).json
    resp_request_create = creator_client.post(
        f"{urls['BASE_URL']}/{draft1_id}/draft/requests/publish_draft"
    ).json

    record_resp_after_create = creator_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true"
    ).json

    creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )

    def find_request_type(requests, type_) -> dict | None:
        for request in requests:
            if request["type_id"] == type_:
                return request
        return None

    record_resp_with_request = receiver_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true"
    ).json

    assert find_request_type(
        record_resp_no_request["expanded"]["request_types"], "publish_draft"
    )

    assert (
        find_request_type(
            record_resp_with_request["expanded"]["request_types"], "publish_draft"
        )
        is None
    )

    assert (
        find_request_type(
            record_resp_after_create["expanded"]["request_types"], "publish_draft"
        )
        is None
    )
