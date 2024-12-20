#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from thesis.records.api import ThesisRecord

from tests.test_requests.utils import link2testclient


# todo since inline is now the default way to create records, these might be redundant
def test_record(
    logged_client,
    record_factory,
    users,
    urls,
    create_request_by_link,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator_client)
    resp_request_create = create_request_by_link(
        creator_client, record1, "delete_published_record"
    )
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    record = receiver_client.get(f"{urls['BASE_URL']}{record1.json['id']}?expand=true")
    delete = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )
    ThesisRecord.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 0


def test_draft(
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

    resp_request_create = create_request_by_link(
        creator_client, draft1, "publish_draft"
    )
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    delete = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )
    ThesisRecord.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 1
