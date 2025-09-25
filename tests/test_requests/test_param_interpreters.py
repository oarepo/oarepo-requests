#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_oarepo.fixtures import LoggedClient


def _init(
    users, logged_client, draft_factory, submit_request, urls
) -> tuple[LoggedClient, LoggedClient]:
    user1 = users[0]
    user2 = users[1]

    user1_client = logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = draft_factory(user1.identity, custom_workflow="different_recipients")
    draft2 = draft_factory(user2.identity, custom_workflow="different_recipients")

    submit_request(
        user1.identity, draft1["id"], "publish_draft"
    )  # recipient should be 2
    submit_request(
        user2.identity, draft2["id"], "another_topic_updating"
    )  # should be 1

    search_unfiltered = user2_client.get(urls["BASE_URL_REQUESTS"])
    assert len(search_unfiltered.json["hits"]["hits"]) == 2
    return user1_client, user2_client


def test_receiver_param_interpreter(
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    search_clear,
):
    user1_client, user2_client = _init(
        users, logged_client, draft_factory, submit_request_on_draft, urls
    )
    search_receiver_only = user2_client.get(
        f"{urls['BASE_URL_REQUESTS']}?assigned=true"
    )  # creator of 1 and recipient of 2
    assert len(search_receiver_only.json["hits"]["hits"]) == 1
    assert search_receiver_only.json["hits"]["hits"][0]["receiver"] == {"user": "2"}
    assert search_receiver_only.json["hits"]["hits"][0]["type"] == "publish_draft"


def test_owner_param_interpreter(
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    search_clear,
):
    user1_client, user2_client = _init(
        users, logged_client, draft_factory, submit_request_on_draft, urls
    )

    search_user1_only = user1_client.get(f"{urls['BASE_URL_REQUESTS']}?mine=true")
    search_user2_only = user2_client.get(f"{urls['BASE_URL_REQUESTS']}?mine=true")

    assert len(search_user1_only.json["hits"]["hits"]) == 1
    assert len(search_user2_only.json["hits"]["hits"]) == 1

    assert search_user1_only.json["hits"]["hits"][0]["created_by"] == {"user": "1"}
    assert search_user1_only.json["hits"]["hits"][0]["type"] == "publish_draft"

    assert search_user2_only.json["hits"]["hits"][0]["created_by"] == {"user": "2"}
    assert search_user2_only.json["hits"]["hits"][0]["type"] == "another_topic_updating"

    # mine requests should be in all=true as well
    search_user1_only = user1_client.get(f"{urls['BASE_URL_REQUESTS']}?all=true")
    for hit in search_user1_only.json["hits"]["hits"]:
        assert hit["created_by"] == {"user": "1"} or hit["receiver"] == {"user": "1"}


def test_open_param_interpreter(
    logged_client,
    users,
    urls,
    draft_factory,
    create_request_on_draft,
    submit_request_on_draft,
    link2testclient,
    search_clear,
):
    user1 = users[0]
    user2 = users[1]

    logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = draft_factory(user1.identity)
    draft2 = draft_factory(user1.identity)
    draft3 = draft_factory(user2.identity)
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]
    draft3_id = draft3["id"]

    submit_request_on_draft(user1.identity, draft1_id, "publish_draft")
    submit_request_on_draft(user1.identity, draft2_id, "publish_draft")
    create_request_on_draft(user2.identity, draft3_id, "publish_draft")

    read = user2_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true")
    user2_client.post(
        link2testclient(
            read.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )

    search_unfiltered = user2_client.get(urls["BASE_URL_REQUESTS"]).json["hits"]["hits"]
    search_open = user2_client.get(f"{urls['BASE_URL_REQUESTS']}?is_open=true").json[
        "hits"
    ]["hits"]
    search_closed = user2_client.get(
        f"{urls['BASE_URL_REQUESTS']}?is_closed=true"
    ).json["hits"]["hits"]

    assert len(search_unfiltered) == 3
    assert len(search_open) == 2
    assert len(search_closed) == 1


# TODO: perhaps test with groups too so we test extracting more references from identity here;
#  tested in communities with community_role
