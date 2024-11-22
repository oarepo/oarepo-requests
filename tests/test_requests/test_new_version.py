#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from thesis.records.api import ThesisDraft, ThesisRecord

from tests.test_requests.utils import link_api2testclient


def test_new_version_autoaccept(
    vocab_cf,
    logged_client,
    users,
    urls,
    new_version_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)

    new_version_direct = creator_client.post(
        f"{urls['BASE_URL']}{record1['id']}/versions",
    )
    assert new_version_direct.status_code == 403

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    assert "draft_record:links:self" in request["payload"]
    assert "draft_record:links:self_html" in request["payload"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    # new_version action worked?
    search = creator_client.get(
        f'user{urls["BASE_URL"]}',
    ).json["hits"]["hits"]
    assert len(search) == 2
    assert search[0]["id"] != search[1]["id"]
    assert search[0]["parent"]["id"] == search[1]["parent"]["id"]


def test_new_version_files(
    vocab_cf,
    logged_client,
    users,
    urls,
    new_version_data_function,
    record_with_files_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_with_files_factory(creator.identity)
    record2 = record_with_files_factory(creator.identity)

    resp_request_create1 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json={
            **new_version_data_function(record1["id"]),
            "payload": {"keep_files": "true"},
        },
    )
    resp_request_create2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(record2["id"]),
    )

    resp_request_submit1 = creator_client.post(
        link_api2testclient(resp_request_create1.json["links"]["actions"]["submit"]),
    )
    resp_request_submit2 = creator_client.post(
        link_api2testclient(resp_request_create2.json["links"]["actions"]["submit"]),
    )

    ThesisDraft.index.refresh()
    draft_search = creator_client.get(f"/user/thesis/").json["hits"][
        "hits"
    ]  # a link is in another pull request for now
    new_version_1 = [
        x
        for x in draft_search
        if x["parent"]["id"] == record1.parent["id"] and x["state"] == "draft"
    ]
    new_version_2 = [
        x
        for x in draft_search
        if x["parent"]["id"] == record2.parent["id"] and x["state"] == "draft"
    ]

    assert len(new_version_1) == 1
    assert len(new_version_2) == 1

    record1 = creator_client.get(
        f"{urls['BASE_URL']}{new_version_1[0]['id']}/draft/files",
    ).json
    record2 = creator_client.get(
        f"{urls['BASE_URL']}{new_version_2[0]['id']}/draft/files",
    ).json

    assert len(record1["entries"]) == 1
    assert len(record2["entries"]) == 0


def test_redirect_url(
    vocab_cf,
    logged_client,
    users,
    urls,
    new_version_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    record1 = record_factory(creator.identity)

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json

    ThesisDraft.index.refresh()
    draft_search = creator_client.get(f"/user/thesis/").json["hits"][
        "hits"
    ]  # a link is in another pull request for now
    new_version = [
        x
        for x in draft_search
        if x["parent"]["id"] == record1.parent["id"] and x["state"] == "draft"
    ][0]
    assert (
        request["links"]["topic"]["topic_redirect_link"]
        == f"https://127.0.0.1:5000/thesis/{new_version['id']}/edit"
    )
