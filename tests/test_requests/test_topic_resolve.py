#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations


def test_resolve_topic(
    db,
    requests_model,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_on_record,
    record_service,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record1_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    assert resp_request_submit["status"] == "submitted"

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    assert resp.json["expanded"]["topic"] == {
        "id": record1_id,
        "links": {
            "latest_html": f"https://127.0.0.1:5000/api/test-requests/records/{record1_id}/latest",
            "self": f"https://127.0.0.1:5000/api/requests-test/{record1_id}",
            "self_html": f"https://127.0.0.1:5000/api/test-requests/records/{record1_id}",
        },
    }

    receiver_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    receiver_client.post(link2testclient(receiver_read.json["links"]["actions"]["accept"]))
    requests_model.Record.index.refresh()

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {"requests_test": record1_id}

    resp_expanded = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp_expanded.status_code == 200
    assert resp_expanded.json["topic"] == {"requests_test": record1_id}
    assert resp_expanded.json["expanded"]["topic"] == {
        "id": record1_id,
        "links": {},
    }
