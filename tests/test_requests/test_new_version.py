#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

from pytest_oarepo.functions import link2testclient
from thesis.records.api import ThesisDraft, ThesisRecord


def test_new_version_autoaccept(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator_client)

    new_version_direct = creator_client.post(
        f"{urls['BASE_URL']}{record1.json['id']}/versions",
    )
    assert new_version_direct.status_code == 403

    resp_request_submit = submit_request_by_link(creator_client, record1, "new_version")
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit.json["id"]}',
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
    ).json[
        "hits"
    ]["hits"]
    assert len(search) == 2
    assert search[0]["id"] != search[1]["id"]
    assert search[0]["parent"]["id"] == search[1]["parent"]["id"]


def test_new_version_files(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    record_with_files_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_with_files_factory(creator_client)
    record2 = record_with_files_factory(creator_client)

    submit1 = submit_request_by_link(
        creator_client,
        record1,
        "new_version",
        create_additional_data={"payload": {"keep_files": "yes"}},
    )
    submit2 = submit_request_by_link(creator_client, record2, "new_version")

    ThesisDraft.index.refresh()
    draft_search = creator_client.get(f"/user/thesis/").json["hits"][
        "hits"
    ]  # a link is in another pull request for now
    new_version_1 = [
        x
        for x in draft_search
        if x["parent"]["id"] == record1.json["parent"]["id"] and x["state"] == "draft"
    ]
    new_version_2 = [
        x
        for x in draft_search
        if x["parent"]["id"] == record2.json["parent"]["id"] and x["state"] == "draft"
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
    logged_client,
    users,
    urls,
    record_factory,
    submit_request_by_link,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    receiver_client = logged_client(users[1])
    record1 = record_factory(creator_client)
    original_id = record1.json["id"]

    resp_request_submit = submit_request_by_link(creator_client, record1, "new_version")
    original_request_id = resp_request_submit.json["id"]
    # is request accepted and closed?

    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{original_request_id}',
    ).json

    ThesisDraft.index.refresh()
    draft_search = creator_client.get(f"/user/thesis/").json["hits"][
        "hits"
    ]  # a link is in another pull request for now
    new_draft = [
        x
        for x in draft_search
        if x["parent"]["id"] == record1.json["parent"]["id"] and x["state"] == "draft"
    ][0]
    assert (
        link2testclient(request["links"]["ui_redirect_url"], ui=True)
        == f"/thesis/{new_draft['id']}/edit"
    )

    new_draft = creator_client.get(f"{urls['BASE_URL']}{new_draft['id']}/draft")
    publish_request = submit_request_by_link(creator_client, new_draft, "publish_draft")
    receiver_request = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request.json['id']}"
    )
    accept = receiver_client.post(
        link2testclient(receiver_request.json["links"]["actions"]["accept"])
    )

    original_request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{original_request_id}',
    ).json
    assert original_request["topic"] == {
        "thesis": original_id
    }  # check no weird topic kerfluffle happened here
