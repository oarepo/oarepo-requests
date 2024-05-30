from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_delete(
    vocab_cf,
    logged_client,
    record_factory,
    users,
    urls,
    delete_record_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    record3 = record_factory(creator.identity)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    print()

    record = receiver_client.get(f"{urls['BASE_URL']}{record1['id']}?expand=true")
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"]),
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record2["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{record2['id']}?expand=true")
    decline = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"])
    )
    declined_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record3["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = creator_client.get(f"{urls['BASE_URL']}{record3['id']}?expand=true")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = creator_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"]),
    )
    canceled_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"
