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
    publish_request_data_function,
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

    r1 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    resp_request_submit = creator_client.post(
        link2testclient(r1.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )

    r2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    r3 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )

    creator_client.get(link2testclient(r1.json["links"]["actions"]["submit"]))
    creator_client.get(link2testclient(r2.json["links"]["actions"]["submit"]))
    creator_client.get(link2testclient(r3.json["links"]["actions"]["submit"]))

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
    delete_record_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    record3 = record_factory(creator.identity)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    r1 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link2testclient(r1.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{record1['id']}?expand=true")
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )

    r2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    r3 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record2["id"]),
    )

    creator_client.post(link2testclient(r1.json["links"]["actions"]["submit"]))
    creator_client.post(link2testclient(r2.json["links"]["actions"]["submit"]))
    creator_client.post(link2testclient(r3.json["links"]["actions"]["submit"]))

    resp1 = creator_client.get(f"{urls['BASE_URL']}{record1['id']}/requests").json[
        "hits"
    ]["hits"]
    resp2 = creator_client.get(f"{urls['BASE_URL']}{record2['id']}/requests").json[
        "hits"
    ]["hits"]
    resp3 = creator_client.get(f"{urls['BASE_URL']}{record3['id']}/requests").json[
        "hits"
    ]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0
