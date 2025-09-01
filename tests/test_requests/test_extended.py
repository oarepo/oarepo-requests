#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_requests.records.api import RequestEvent
from pytest_oarepo.functions import clear_babel_context, is_valid_subdict


def test_listing(
    requests_model,
    logged_client,
    users,
    urls,
    create_request_on_draft,
    draft_factory,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft2 = draft_factory(creator.identity)

    create_request_on_draft(creator.identity, draft1["id"], "publish_draft")
    create_request_on_draft(creator.identity, draft2["id"], "publish_draft")

    requests_model.Draft.index.refresh()
    search = creator_client.get(
        urls["BASE_URL_REQUESTS"],
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )


def test_read_extended(
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    serialization_result,
    ui_serialization_result,
    draft_factory,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft_id = draft1["id"]

    resp_request_submit = submit_request_on_draft(creator.identity, draft_id, "publish_draft")

    old_call = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    new_call = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_submit['id']}",
    )
    new_call2 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_submit['id']}",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    assert is_valid_subdict(
        serialization_result(draft_id, resp_request_submit["id"]),
        new_call.json,
    )
    assert is_valid_subdict(
        ui_serialization_result(draft_id, resp_request_submit["id"]),
        new_call2.json,
    )


def test_update_self_link(
    logged_client,
    users,
    urls,
    serialization_result,
    submit_request_on_draft,
    ui_serialization_result,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    resp_request_submit = submit_request_on_draft(creator.identity, draft1_id, "publish_draft")

    read_before = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
    )
    read_from_record = creator_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true",
    )
    link_to_extended = link2testclient(read_from_record.json["expanded"]["requests"][0]["links"]["self"])

    assert link_to_extended.startswith(f"{urls['BASE_URL_REQUESTS']}extended")
    update_extended = creator_client.put(
        link_to_extended,
        json={"title": "lalala"},
    )
    assert update_extended.status_code == 200
    read_after = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
    )
    assert read_before.json["title"] == ""
    assert read_after.json["title"] == "lalala"


def test_events_resource(
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    serialization_result,
    ui_serialization_result,
    events_resource_data,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    resp_request_submit = submit_request_on_draft(creator.identity, draft1_id, "publish_draft")

    read_before = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    read_from_record = creator_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true",
    )

    comments_link = link2testclient(read_from_record.json["expanded"]["requests"][0]["links"]["comments"])
    timeline_link = link2testclient(read_from_record.json["expanded"]["requests"][0]["links"]["timeline"])

    assert comments_link.startswith("/requests/extended")
    assert timeline_link.startswith("/requests/extended")

    comments_extended = creator_client.post(
        comments_link,
        json=events_resource_data,
    )
    assert comments_extended.status_code == 201
    comment = creator_client.get(
        f"{comments_link}/{comments_extended.json['id']}",
    )
    assert comment.status_code == 200
    RequestEvent.index.refresh()
    comments_extended_timeline = creator_client.get(
        timeline_link,
    )
    assert comments_extended_timeline.status_code == 200
    assert len(comments_extended_timeline.json["hits"]["hits"]) == 1
