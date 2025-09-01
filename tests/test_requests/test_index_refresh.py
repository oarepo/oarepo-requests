#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations


def test_search(
    logged_client,
    users,
    urls,
    create_request_on_draft,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)

    resp_request_create = create_request_on_draft(creator.identity, draft1["id"], "publish_draft")
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
