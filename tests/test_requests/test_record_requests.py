#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link2testclient


def test_read_requests_on_draft(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    create_request_by_link,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    draft2 = create_draft_via_resource(creator_client)
    draft3 = create_draft_via_resource(creator_client)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_submit = submit_request_by_link(
        creator_client, draft1, "publish_draft"
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        )
    )

    r2 = create_request_by_link(creator_client, draft1, "publish_draft")
    r3 = create_request_by_link(creator_client, draft2, "publish_draft")

    resp1 = creator_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft/requests"
    ).json["hits"]["hits"]
    resp2 = creator_client.get(
        f"{urls['BASE_URL']}{draft2.json['id']}/draft/requests"
    ).json["hits"]["hits"]
    resp3 = creator_client.get(
        f"{urls['BASE_URL']}{draft3.json['id']}/draft/requests"
    ).json["hits"]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0


def test_read_requests_on_record(
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_by_link,
    create_request_by_link,
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
    resp_request_submit = submit_request_by_link(
        creator_client, record1, "delete_published_record"
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{record1.json['id']}?expand=true")
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )
    r2 = create_request_by_link(creator_client, record1, "delete_published_record")
    r3 = create_request_by_link(creator_client, record2, "delete_published_record")

    resp1 = creator_client.get(f"{urls['BASE_URL']}{record1.json['id']}/requests").json[
        "hits"
    ]["hits"]
    resp2 = creator_client.get(f"{urls['BASE_URL']}{record2.json['id']}/requests").json[
        "hits"
    ]["hits"]
    resp3 = creator_client.get(f"{urls['BASE_URL']}{record3.json['id']}/requests").json[
        "hits"
    ]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0
