from invenio_requests.records.api import RequestEvent

from thesis.records.api import ThesisDraft

from .utils import is_valid_subdict, link_api2testclient


def test_listing(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    draft2 = creator_client.post(urls["BASE_URL"], json={})

    creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    ThesisDraft.index.refresh()
    search = creator_client.get(
        urls["BASE_URL_REQUESTS"],
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )


def test_read_extended(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    draft_id = draft1.json["id"]

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft_id),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    old_call = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    new_call = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}",
    )
    new_call2 = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    assert is_valid_subdict(
        serialization_result(draft_id, resp_request_create.json["id"]),
        new_call.json,
    )
    assert is_valid_subdict(
        ui_serialization_result(draft_id, resp_request_create.json["id"]),
        new_call2.json,
    )


def test_update_self_link(
    logged_client,
    example_topic_draft,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(example_topic_draft["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    read_before = creator_client.get(
        link_api2testclient(resp_request_submit.json["links"]["self"]),
    )
    read_from_record = creator_client.get(
        f"{urls['BASE_URL']}{example_topic_draft['id']}/draft?expand=true",
    )
    link_to_extended = link_api2testclient(
        read_from_record.json["requests"][0]["links"]["self"]
    )

    assert link_to_extended.startswith(f"{urls['BASE_URL_REQUESTS']}extended")
    update_extended = creator_client.put(
        link_to_extended,
        json={"title": "lalala"},
    )
    assert update_extended.status_code == 200
    read_after = creator_client.get(
        link_api2testclient(resp_request_submit.json["links"]["self"]),
    )
    assert read_before.json["title"] == ""
    assert read_after.json["title"] == "lalala"


def test_events_resource(
    example_topic_draft,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    events_resource_data,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(example_topic_draft["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    read_before = creator_client.get(
        link_api2testclient(resp_request_submit.json["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    read_from_record = creator_client.get(
        f"{urls['BASE_URL']}{example_topic_draft['id']}/draft?expand=true",
    )

    comments_link = link_api2testclient(
        read_from_record.json["requests"][0]["links"]["comments"]
    )
    timeline_link = link_api2testclient(
        read_from_record.json["requests"][0]["links"]["timeline"]
    )

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
