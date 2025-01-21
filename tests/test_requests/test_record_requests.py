#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from pytest_oarepo.functions import link2testclient
from thesis.records.api import ThesisDraft, ThesisRecord


def test_read_requests_on_draft(
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    create_request_on_draft,
    draft_factory,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft2 = draft_factory(creator.identity)
    draft3 = draft_factory(creator.identity)
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]
    draft3_id = draft3["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1_id}/draft?expand=true"
    )
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        )
    )

    r2 = create_request_on_draft(creator.identity, draft1_id, "publish_draft")
    r3 = create_request_on_draft(creator.identity, draft2_id, "publish_draft")

    resp1 = creator_client.get(
        f"{urls['BASE_URL']}{draft1_id}/draft/requests"
    ).json["hits"]["hits"]
    resp2 = creator_client.get(
        f"{urls['BASE_URL']}{draft2_id}/draft/requests"
    ).json["hits"]["hits"]
    resp3 = creator_client.get(
        f"{urls['BASE_URL']}{draft3_id}/draft/requests"
    ).json["hits"]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0


def test_read_requests_on_record(
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_on_record,
    create_request_on_record,
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
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    resp_request_submit = submit_request_on_record(
        creator.identity, record1_id, "delete_published_record"
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true")
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )
    r2 = create_request_on_record(creator.identity, record1_id, "delete_published_record")
    r3 = create_request_on_record(creator.identity, record2_id, "delete_published_record")

    resp1 = creator_client.get(f"{urls['BASE_URL']}{record1_id}/requests").json[
        "hits"
    ]["hits"]
    resp2 = creator_client.get(f"{urls['BASE_URL']}{record2_id}/requests").json[
        "hits"
    ]["hits"]
    resp3 = creator_client.get(f"{urls['BASE_URL']}{record3_id}/requests").json[
        "hits"
    ]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0
