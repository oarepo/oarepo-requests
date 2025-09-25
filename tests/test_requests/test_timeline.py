#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_requests.records.api import RequestEvent
from pytest_oarepo.functions import clear_babel_context


def test_timeline(
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    user_links,
    link2testclient,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    publish_request_submit_resp = submit_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )

    comment_resp = creator_client.post(
        link2testclient(publish_request_submit_resp["links"]["comments"]),
        json={"payload": {"content": "test"}},
    )
    assert comment_resp.status_code == 201
    RequestEvent.index.refresh()

    timeline_resp = creator_client.get(
        link2testclient(publish_request_submit_resp["links"]["timeline"]),
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1

    # vnd serialization
    timeline_resp = creator_client.get(
        link2testclient(publish_request_submit_resp["links"]["timeline"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1
    comment = timeline_resp.json["hits"]["hits"][0]
    assert (
        comment.items()
        >= {
            "created_by": {
                "reference": {"user": "1"},
                "type": "user",
                "label": "id: 1",
                "links": user_links(1),
            },
            "permissions": {},
            "payload": {"content": "test", "format": "html"},
        }.items()
    )
