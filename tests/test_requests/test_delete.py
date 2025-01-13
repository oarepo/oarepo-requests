#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from thesis.records.api import ThesisDraft, ThesisRecord

from pytest_oarepo.functions import link2testclient


def test_delete(
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_by_link,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator_client)
    record2 = record_factory(creator_client)
    record3 = record_factory(creator_client)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_submit = submit_request_by_link(
        creator_client, record1, "delete_published_record"
    )

    record = receiver_client.get(f"{urls['BASE_URL']}{record1.json['id']}?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    assert (
        link2testclient(delete.json["links"]["ui_redirect_url"], ui=True) == "/thesis/"
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_submit = submit_request_by_link(
        creator_client, record2, "delete_published_record"
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{record2.json['id']}?expand=true")
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        )
    )
    declined_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit.json['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_submit = submit_request_by_link(
        creator_client, record3, "delete_published_record"
    )
    record = creator_client.get(f"{urls['BASE_URL']}{record3.json['id']}?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "cancel"
    }
    cancel = creator_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["cancel"]
        ),
    )
    canceled_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"


def test_delete_draft(
    logged_client,
    draft_factory,
    users,
    urls,
    get_request_link,
    search_clear,
):
    creator_client = logged_client(users[0])

    draft1 = draft_factory(creator_client)
    draft_id = draft1.json["id"]

    read = creator_client.get(f"{urls['BASE_URL']}{draft_id}/draft?expand=true")
    assert read.status_code == 200

    resp_request_create = creator_client.post(
        link2testclient(
            get_request_link(read.json["expanded"]["request_types"], "delete_draft")
        )
    )
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    read_deleted = creator_client.get(f"{urls['BASE_URL']}{draft_id}/draft?expand=true")
    request_after = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )  # autoapprove suggested here
    assert request_after.json["status"] == "accepted"
    assert request_after.json["is_closed"]
    assert (
        link2testclient(request_after.json["links"]["ui_redirect_url"], ui=True)
        == "/thesis/"
    )
    assert read_deleted.status_code == 404
