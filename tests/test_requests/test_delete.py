#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from pytest_oarepo.requests.functions import get_request_create_link


def test_delete(
    requests_model,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_on_record,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    record3 = record_factory(creator.identity)
    record1_id = record1["id"]
    record2_id = record2["id"]
    record3_id = record3["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record1_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )

    record = receiver_client.get(f"{urls['BASE_URL']}/{record1_id}?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = receiver_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]),
    )
    assert link2testclient(delete.json["links"]["ui_redirect_url"], ui=True) == urls["BASE_URL"]

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record2_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    record = receiver_client.get(f"{urls['BASE_URL']}/{record2_id}?expand=true")
    decline = receiver_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["decline"])
    )
    declined_request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    assert declined_request.json["status"] == "declined"

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record3_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    record = creator_client.get(f"{urls['BASE_URL']}/{record3_id}?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = creator_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["cancel"]),
    )
    canceled_request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    assert canceled_request.json["status"] == "cancelled"


def test_delete_draft(
    logged_client,
    draft_factory,
    users,
    urls,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft_id = draft1["id"]

    read = creator_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true")
    assert read.status_code == 200

    resp_request_create = creator_client.post(
        link2testclient(get_request_create_link(read.json["expanded"]["request_types"], "delete_draft"))
    )
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    read_deleted = creator_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true")
    request_after = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )  # autoapprove suggested here
    assert request_after.json["status"] == "accepted"
    assert request_after.json["is_closed"]
    assert link2testclient(request_after.json["links"]["ui_redirect_url"], ui=True) == f"{urls['BASE_URL']}/"
    assert read_deleted.status_code == 404
