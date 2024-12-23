#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from invenio_requests.records.api import RequestEvent

from tests.test_requests.test_create_inmodel import pick_request_type
from tests.test_requests.utils import link2testclient


def test_timeline(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    user_links,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)
    link = link2testclient(
        pick_request_type(draft1.json["expanded"]["request_types"], "publish_draft")[
            "links"
        ]["actions"]["create"]
    )

    publish_request_resp = creator_client.post(link)
    assert publish_request_resp.status_code == 201

    publish_request_submit_resp = creator_client.post(
        link2testclient(publish_request_resp.json["links"]["actions"]["submit"]),
    )
    assert publish_request_submit_resp.status_code == 200

    comment_resp = creator_client.post(
        link2testclient(publish_request_resp.json["links"]["comments"]),
        json={"payload": {"content": "test"}},
    )
    assert comment_resp.status_code == 201
    RequestEvent.index.refresh()

    timeline_resp = creator_client.get(
        link2testclient(publish_request_resp.json["links"]["timeline"]),
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1

    # vnd serialization
    timeline_resp = creator_client.get(
        link2testclient(publish_request_resp.json["links"]["timeline"]),
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
