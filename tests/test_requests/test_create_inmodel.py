#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

from thesis.records.api import ThesisRecord

from thesis.records.api import ThesisDraft


# todo since inline is now the default way to create records, these might be redundant
def test_record(
    logged_client,
    record_factory,
    users,
    urls,
    create_request_on_record,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]
    resp_request_create = create_request_on_record(
        creator.identity, record1_id, "delete_published_record"
    )
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )

    record = receiver_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true")
    delete = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 0


def test_draft(
    logged_client,
    users,
    urls,
    draft_factory,
    create_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    resp_request_create = create_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1_id}/draft?expand=true"
    ).json
    receiver_client.post(
        link2testclient(record["expanded"]["requests"][0]["links"]["actions"]["accept"])
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"]).json
    assert len(lst["hits"]["hits"]) == 1
