import pytest

from oarepo_requests.errors import OpenRequestAlreadyExists

from .utils import link_api2testclient


def test_can_create(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    draft2 = create_draft_via_resource(creator_client)

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    with pytest.raises(OpenRequestAlreadyExists):
        creator_client.post(  # create request after create
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft1.json["id"]),
        )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    with pytest.raises(OpenRequestAlreadyExists):
        creator_client.post(  # create request after submit
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft1.json["id"]),
        )

    # should still be creatable for draft2
    create_for_request_draft2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    assert create_for_request_draft2.status_code == 201

    # try declining the request for draft2, we should be able to create again then
    resp_request_submit = creator_client.post(
        link_api2testclient(
            create_for_request_draft2.json["links"]["actions"]["submit"]
        ),
    )

    with pytest.raises(OpenRequestAlreadyExists):
        create_for_request_draft2 = creator_client.post(
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft2.json["id"]),
        )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft2.json['id']}/draft?expand=true"
    )
    decline = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )

    resp_request_create_again = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    assert resp_request_create_again.status_code == 201


def test_can_possibly_create(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    draft2 = create_draft_via_resource(creator_client)

    record_resp_no_request = creator_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    record_resp_after_create = creator_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    def find_request_type(requests, type):
        for request in requests:
            if request["type_id"] == type:
                return request
        return None

    record_resp_with_request = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )

    assert find_request_type(
        record_resp_no_request.json["expanded"]["request_types"], "publish_draft"
    )

    assert (
        find_request_type(
            record_resp_with_request.json["expanded"]["request_types"], "publish_draft"
        )
        is None
    )

    assert (
        find_request_type(
            record_resp_after_create.json["expanded"]["request_types"], "publish_draft"
        )
        is None
    )
