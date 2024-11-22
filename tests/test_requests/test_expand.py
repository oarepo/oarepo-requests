#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from tests.test_requests.test_create_inmodel import pick_request_type
from tests.test_requests.utils import link_api2testclient


def test_requests_field(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    link = link_api2testclient(
        pick_request_type(draft1.json["expanded"]["request_types"], "publish_draft")[
            "links"
        ]["actions"]["create"]
    )

    resp_request_create = creator_client.post(link)
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    expanded_record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )

    assert "requests" not in record.json.get("expanded", {})
    assert "requests" in expanded_record.json["expanded"]


def test_autoaccept_receiver(
    vocab_cf,
    logged_client,
    users,
    urls,
    edit_record_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    id_ = record1["id"]
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=edit_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}?expand=true'
    ).json
    assert request["expanded"]["receiver"] == {"auto_approve": "true"}
