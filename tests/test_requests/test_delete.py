from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_delete(
    logged_client_request,
    record_factory,
    identity_simple,
    users,
    urls,
    delete_record_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    record1 = record_factory(identity_simple)
    record2 = record_factory(identity_simple)
    record3 = record_factory(identity_simple)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = logged_client_request(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    print()

    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{record1['id']}"
    )
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = logged_client_request(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"]),
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = logged_client_request(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record2["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{record2['id']}"
    )
    decline = logged_client_request(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"]),
    )
    declined_request = logged_client_request(
        creator, "get", f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record3["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = logged_client_request(creator, "get", f"{urls['BASE_URL']}{record3['id']}")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = logged_client_request(
        creator,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"]),
    )
    canceled_request = logged_client_request(
        creator, "get", f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"
