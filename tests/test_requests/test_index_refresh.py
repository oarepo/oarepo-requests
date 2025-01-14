#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from tests.test_requests.utils import link2testclient


def test_search(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    # should work without refreshing requests index
    requests_search = creator_client.get(urls["BASE_URL_REQUESTS"]).json

    assert len(requests_search["hits"]["hits"]) == 1

    link = link2testclient(requests_search["hits"]["hits"][0]["links"]["self"])
    extended_link = link.replace("/requests/", "/requests/extended/")

    update = creator_client.put(
        extended_link,
        json={"title": "tralala"},
    )

    requests_search = creator_client.get(urls["BASE_URL_REQUESTS"]).json
    assert requests_search["hits"]["hits"][0]["title"] == "tralala"
