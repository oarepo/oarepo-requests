from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import BASE_URL, BASE_URL_REQUESTS, link_api2testclient


def test_delete(client_factory, record_factory, identity_simple, users, monkeypatch):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    def data(receiver, record):
        return {
            "receiver": {"user": receiver.id},
            "request_type": "delete_record",
            "topic": {"thesis": record["id"]},
        }

    record1 = record_factory()
    record2 = record_factory()
    record3 = record_factory()
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(BASE_URL)
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, record1)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = receiver_client.get(f"{BASE_URL}{record1['id']}")
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"])
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(BASE_URL)
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, record2)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = receiver_client.get(f"{BASE_URL}{record2['id']}")
    decline = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"])
    )
    declined_request = creator_client.get(
        f"{BASE_URL_REQUESTS}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, record3)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = creator_client.get(f"{BASE_URL}{record3['id']}")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = creator_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"])
    )
    canceled_request = creator_client.get(
        f"{BASE_URL_REQUESTS}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"


"""
def test_errors(client_factory, record_factory, identity_simple, users, monkeypatch):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    def data(receiver, record):
        return {
            "receiver": {"user": receiver.id},
            "request_type": "delete_record",
            "topic": {"thesis": record["id"]},
        }

    record1 = record_factory()
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(BASE_URL)

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, record1)
    )
    with pytest.raises(OpenRequestAlreadyExists):
        creator_client.post(f"{BASE_URL_REQUESTS}", json=data(receiver, record1))
"""
