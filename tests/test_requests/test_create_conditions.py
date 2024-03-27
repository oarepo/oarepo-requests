import pytest

from oarepo_requests.errors import OpenRequestAlreadyExists

from .utils import link_api2testclient


def test_can_create(
    logged_client_request,
    identity_simple,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    draft1 = logged_client_request(creator, "post", urls["BASE_URL"], json={})
    draft2 = logged_client_request(creator, "post", urls["BASE_URL"], json={})

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    with pytest.raises(OpenRequestAlreadyExists):
        resp_request_create_duplicated = logged_client_request(
            creator,
            "post",
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft1.json["id"]),
        )

    # should still be creatable for draft2
    create_for_request_draft2 = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    assert create_for_request_draft2.status_code == 201

    # try declining the request for draft2, we should be able to create again then
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(
            create_for_request_draft2.json["links"]["actions"]["submit"]
        ),
    )

    with pytest.raises(OpenRequestAlreadyExists):
        create_for_request_draft2 = logged_client_request(
            creator,
            "post",
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft2.json["id"]),
        )
    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft2.json['id']}/draft"
    )
    decline = logged_client_request(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"]),
    )

    resp_request_create_again = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    assert resp_request_create_again.status_code == 201


def test_can_possibly_create(
    logged_client_request,
    identity_simple,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    draft1 = logged_client_request(creator, "post", urls["BASE_URL"], json={})
    draft2 = logged_client_request(creator, "post", urls["BASE_URL"], json={})

    record_resp_no_request = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft1.json['id']}/draft"
    )
    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    def find_request_type(requests, type):
        for request in requests:
            if request["type_id"] == type:
                return request
        return None

    record_resp_with_request = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft1.json['id']}/draft"
    )
    record_resp_draft2 = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft2.json['id']}/draft"
    )
    assert find_request_type(
        record_resp_no_request.json["request_types"], "thesis_publish_draft"
    )
    assert find_request_type(
        record_resp_draft2.json["request_types"], "thesis_publish_draft"
    )
    assert (
        find_request_type(
            record_resp_with_request.json["request_types"], "thesis_publish_draft"
        )
        is None
    )
