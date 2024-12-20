#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from tests.test_requests.utils import link2testclient


def test_requests_field(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    create_request_by_link,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)

    resp_request_create = create_request_by_link(creator_client, draft1, "publish_draft")
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    expanded_record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )

    assert "requests" not in record.json.get("expanded", {})
    assert "requests" in expanded_record.json["expanded"]


def test_autoaccept_receiver(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator_client)
    resp_request_submit = submit_request_by_link(creator_client, record1, "edit_published_record")
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit.json["id"]}?expand=true'
    ).json
    assert request["expanded"]["receiver"] == {"auto_approve": "true"}
