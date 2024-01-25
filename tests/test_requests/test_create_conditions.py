import pytest

from oarepo_requests.errors import OpenRequestAlreadyExists

from .utils import link_api2testclient


def data(receiver, record):
    return {
        "receiver": {"user": receiver.id},
        "request_type": "non_duplicable",
        "topic": {"thesis_draft": record.json["id"]},
    }


def test_can_create(client_factory, identity_simple, users, urls):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    draft1 = creator_client.post(urls["BASE_URL"], json={})

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"], json=data(receiver, draft1)
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )

    with pytest.raises(OpenRequestAlreadyExists):
        resp_request_create2 = creator_client.post(
            urls["BASE_URL_REQUESTS"], json=data(receiver, draft1)
        )


def test_can_possibly_create(client_factory, identity_simple, users, urls):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    record_resp_no_request = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"], json=data(receiver, draft1)
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )

    def find_request_type(requests, type):
        for request in requests:
            if request["type"] == type:
                return request
        return None

    record_resp_request = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    assert find_request_type(
        record_resp_no_request.json["request_types"], "non_duplicable"
    )
    assert (
        find_request_type(record_resp_request.json["request_types"], "non_duplicable")
        is None
    )
