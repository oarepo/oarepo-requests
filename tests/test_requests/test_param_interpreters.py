#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import json
from tests.test_requests.utils import link2testclient


def _init(users, logged_client, create_draft_via_resource, submit_request, urls):
    user1 = users[0]
    user2 = users[1]

    user1_client = logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = create_draft_via_resource(
        user1_client, custom_workflow="different_recipients"
    )
    draft2 = create_draft_via_resource(
        user2_client, custom_workflow="different_recipients"
    )

    submit_response_user1 = submit_request(
        user1_client, draft1, "publish_draft"
    )  # recipient should be 2
    submit_response_user2 = submit_request(
        user2_client, draft2, "another_topic_updating"
    )  # should be 1

    search_unfiltered = user2_client.get(urls["BASE_URL_REQUESTS"])
    assert len(search_unfiltered.json["hits"]["hits"]) == 2
    return user1_client, user2_client


def test_receiver_param_interpreter(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    submit_request_by_link,
    search_clear,
):
    user1_client, user2_client = _init(
        users, logged_client, create_draft_via_resource, submit_request_by_link, urls
    )
    search_receiver_only = user2_client.get(
        f'{urls["BASE_URL_REQUESTS"]}?assigned=true'
    )  # creator of 1 and recipient of 2
    assert len(search_receiver_only.json["hits"]["hits"]) == 1
    assert search_receiver_only.json["hits"]["hits"][0]["receiver"] == {"user": "2"}
    assert search_receiver_only.json["hits"]["hits"][0]["type"] == "publish_draft"


def test_owner_param_interpreter(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    submit_request_by_link,
    search_clear,
):
    user1_client, user2_client = _init(
        users, logged_client, create_draft_via_resource, submit_request_by_link, urls
    )

    search_user1_only = user1_client.get(f'{urls["BASE_URL_REQUESTS"]}?mine=true')
    search_user2_only = user2_client.get(f'{urls["BASE_URL_REQUESTS"]}?mine=true')

    assert len(search_user1_only.json["hits"]["hits"]) == 1
    assert len(search_user2_only.json["hits"]["hits"]) == 1

    assert search_user1_only.json["hits"]["hits"][0]["created_by"] == {"user": "1"}
    assert search_user1_only.json["hits"]["hits"][0]["type"] == "publish_draft"

    assert search_user2_only.json["hits"]["hits"][0]["created_by"] == {"user": "2"}
    assert search_user2_only.json["hits"]["hits"][0]["type"] == "another_topic_updating"

    # mine requests should be in all=true as well
    search_user1_only = user1_client.get(f'{urls["BASE_URL_REQUESTS"]}?all=true')
    print(json.dumps(search_user1_only.json))
    for hit in search_user1_only.json["hits"]["hits"]:
        assert hit['created_by'] == {"user": "1"} or hit['receiver'] == {"user": "1"}

def test_open_param_interpreter(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    create_request_by_link,
    submit_request_by_link,
    search_clear,
):
    user1 = users[0]
    user2 = users[1]

    user1_client = logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = create_draft_via_resource(user1_client)
    draft2 = create_draft_via_resource(user1_client)
    draft3 = create_draft_via_resource(user2_client)

    submit_response_user1 = submit_request_by_link(
        user1_client, draft1, "publish_draft"
    )
    submit_response_user2 = submit_request_by_link(
        user1_client, draft2, "publish_draft"
    )
    create_response = create_request_by_link(user2_client, draft3, "publish_draft")

    read = user2_client.get(f'{urls["BASE_URL"]}{draft1.json["id"]}/draft?expand=true')
    publish = user2_client.post(
        link2testclient(
            read.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )

    search_unfiltered = user2_client.get(urls["BASE_URL_REQUESTS"]).json["hits"]["hits"]
    search_open = user2_client.get(f'{urls["BASE_URL_REQUESTS"]}?is_open=true').json[
        "hits"
    ]["hits"]
    search_closed = user2_client.get(
        f'{urls["BASE_URL_REQUESTS"]}?is_closed=true'
    ).json["hits"]["hits"]

    assert len(search_unfiltered) == 3
    assert len(search_open) == 2
    assert len(search_closed) == 1


# todo perhaps test with groups too so we test extracting more references from identity here; tested in communities with community_role
