#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_requests.records.api import RequestEvent

from oarepo_requests.types.events import TopicDeleteEventType

"""
# TODO: werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'requests_test.search_versions' with values ['page', 'size', 'sort']. Did you mean 'invenio_requests.static' instead? is an oarepo-ui todo
def test_cascade_update(
    requests_model,
    logged_client,
    users,
    urls,
    draft_factory,
    check_publish_topic_update,
    create_request_on_draft,
    submit_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity, custom_workflow="cascade_update")
    draft2 = draft_factory(creator.identity, custom_workflow="cascade_update")
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]

    publish_request_create = submit_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
    another_request_create = submit_request_on_draft(
        creator.identity, draft1_id, "another_topic_updating"
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true"
    ).json
    receiver_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    publish_request_on_second_draft = create_request_on_draft(
        creator.identity, draft2_id, "publish_draft"
    )

    record = receiver_client.get(
        f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true"
    ).json
    receiver_client.post(
        link2testclient(
            record["expanded"]["requests"][1]["links"]["actions"]["accept"]
        ),
    )

    check_publish_topic_update(creator_client, urls, record, publish_request_create)
    check_publish_topic_update(creator_client, urls, draft1, another_request_create)

    second_draft_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request_on_second_draft['id']}"
    ).json
    assert second_draft_request["topic"] == {
        "requests_test_draft": draft2_id
    }  # check request on the other draft is unchanged


def test_cascade_cancel(
    requests_model,
    logged_client,
    users,
    urls,
    record_factory,
    create_request_on_record,
    submit_request_on_record,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = record_factory(creator.identity, custom_workflow="cascade_update")
    draft2 = record_factory(creator.identity, custom_workflow="cascade_update")
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]

    r1 = submit_request_on_record(creator.identity, draft1_id, "publish_draft")
    r2 = create_request_on_record(creator.identity, draft1_id, "another_topic_updating")
    r3 = submit_request_on_record(creator.identity, draft2_id, "publish_draft")

    submit_request_on_record(creator.identity, draft1_id, "delete_published_record")

    r1_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r1['id']}").json
    r2_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r2['id']}").json
    r3_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r3['id']}").json

    assert r1_read["status"] == "cancelled"
    assert r2_read["status"] == "cancelled"
    assert r3_read["status"] == "submitted"

    RequestEvent.index.refresh()
    events1 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r1['id']}/timeline"
    ).json["hits"]["hits"]
    events2 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r2['id']}/timeline"
    ).json["hits"]["hits"]
    events3 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r3['id']}/timeline"
    ).json["hits"]["hits"]

    topic_deleted_events1 = [
        e for e in events1 if e["type"] == TopicDeleteEventType.type_id
    ]
    topic_deleted_events2 = [
        e for e in events2 if e["type"] == TopicDeleteEventType.type_id
    ]
    topic_deleted_events3 = [
        e for e in events3 if e["type"] == TopicDeleteEventType.type_id
    ]
    assert len(topic_deleted_events1) == 1
    assert len(topic_deleted_events2) == 1
    assert len(topic_deleted_events3) == 0
"""
