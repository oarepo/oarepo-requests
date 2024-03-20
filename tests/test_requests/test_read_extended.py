from .utils import is_valid_subdict, link_api2testclient


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
