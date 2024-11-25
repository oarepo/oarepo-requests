#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from invenio_requests.records.api import RequestEvent

from oarepo_requests.types.events import TopicDeleteEventType

from .utils import link_api2testclient


def test_cascade_update(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    another_topic_updating_request_function,
    create_draft_via_resource,
    check_publish_topic_update,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")
    draft2 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")

    publish_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    another_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=another_topic_updating_request_function(draft1.json["id"]),
    )
    publish_request_on_second_draft = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(publish_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    publish = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )

    check_publish_topic_update(creator_client, urls, record, publish_request_create)
    check_publish_topic_update(creator_client, urls, record, another_request_create)

    second_draft_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request_on_second_draft.json['id']}"
    )
    assert second_draft_request.json["topic"] == {
        "thesis_draft": draft2.json["id"]
    }  # check request on the other draft is unchanged


def test_cascade_cancel(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    another_topic_updating_request_function,
    create_draft_via_resource,
    create_request_by_link,
    submit_request_by_link,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")
    draft2 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")

    r1 = submit_request_by_link(creator_client, draft1, "publish_draft")
    r2 = create_request_by_link(creator_client, draft1, "another_topic_updating")
    r3 = submit_request_by_link(creator_client, draft2, "publish_draft")

    delete_request = submit_request_by_link(creator_client, draft1, "delete_draft")

    r1_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r1.json['id']}")
    r2_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r2.json['id']}")
    r3_read = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{r3.json['id']}")

    assert r1_read.json["status"] == "cancelled"
    assert r2_read.json["status"] == "cancelled"
    assert r3_read.json["status"] == "submitted"

    RequestEvent.index.refresh()
    events1 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r1.json['id']}/timeline"
    ).json["hits"]["hits"]
    events2 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r2.json['id']}/timeline"
    ).json["hits"]["hits"]
    events3 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{r3.json['id']}/timeline"
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
