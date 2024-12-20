#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from invenio_requests.records.api import RequestEvent
from tests.test_requests.utils import link2testclient


def test_timeline(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    submit_request_by_link,
    user_links,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)

    publish_request_submit_resp = submit_request_by_link(creator_client, draft1, "publish_draft")

    comment_resp = creator_client.post(
        link2testclient(publish_request_submit_resp.json["links"]["comments"]),
        json={"payload": {"content": "test"}},
    )
    assert comment_resp.status_code == 201
    RequestEvent.index.refresh()

    timeline_resp = creator_client.get(
        link2testclient(publish_request_submit_resp.json["links"]["timeline"]),
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1

    # vnd serialization
    timeline_resp = creator_client.get(
        link2testclient(publish_request_submit_resp.json["links"]["timeline"]),
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
