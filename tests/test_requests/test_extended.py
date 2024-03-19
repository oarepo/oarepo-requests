from .utils import is_valid_subdict, link_api2testclient
from invenio_requests.records.api import RequestEvent

def test_read_extended(
    example_topic_draft,
    client_logged_as,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    search_clear,
):
    receiver = users[1]
    creator_client = client_logged_as(users[0].email)
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(example_topic_draft["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    receiver_client = client_logged_as(users[1].email)
    old_call = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    new_call = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}"
    )
    new_call2 = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    assert is_valid_subdict(
        serialization_result(example_topic_draft["id"], resp_request_create.json["id"]),
        new_call.json,
    )
    assert is_valid_subdict(
        ui_serialization_result(
            example_topic_draft["id"], resp_request_create.json["id"]
        ),
        new_call2.json,
    )


def test_update_self_link(
    example_topic_draft,
    client_logged_as,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    search_clear,
):
    receiver = users[1]
    creator_client = client_logged_as(users[0].email)
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
        f"{urls['BASE_URL']}{example_topic_draft['id']}/draft",
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
    client_logged_as,
    users,
    urls,
    publish_request_data_function,
    serialization_result,
    ui_serialization_result,
    events_resource_data,
    search_clear,
):
    creator_client = client_logged_as(users[0].email)
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
        f"{urls['BASE_URL']}{example_topic_draft['id']}/draft",
    )

    comments_link = link_api2testclient(read_from_record.json['requests'][0]["links"]["comments"])
    timeline_link = link_api2testclient(read_from_record.json['requests'][0]["links"]["timeline"])

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





