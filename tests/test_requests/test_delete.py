from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient



def test_delete(
    logged_client_post,
    record_factory,
    identity_simple,
    users,
    urls,
    delete_record_data_function,
):
    creator = users[0]
    receiver = users[1]
    record1 = record_factory()
    record2 = record_factory()
    record3 = record_factory()
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = logged_client_post(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 3

    resp_request_create = logged_client_post(creator, "post",
        urls["BASE_URL_REQUESTS"], json=delete_record_data_function(receiver.id, record1["id"])
    )
    resp_request_submit = logged_client_post(creator, "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    print()

    record = logged_client_post(receiver, "get", f"{urls['BASE_URL']}{record1['id']}")
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    delete = logged_client_post(receiver, "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"])
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = logged_client_post(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 2

    resp_request_create = logged_client_post(creator, "post",
        urls["BASE_URL_REQUESTS"], json=delete_record_data_function(receiver.id, record2["id"])
    )
    resp_request_submit = logged_client_post(creator, "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = logged_client_post(receiver, "get",f"{urls['BASE_URL']}{record2['id']}")
    decline = logged_client_post(receiver, "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"])
    )
    declined_request = logged_client_post(creator, "get",
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_create = logged_client_post(creator, "post",
        urls["BASE_URL_REQUESTS"], json=delete_record_data_function(receiver.id, record3["id"])
    )
    resp_request_submit = logged_client_post(creator, "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = logged_client_post(creator, "get",f"{urls['BASE_URL']}{record3['id']}")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = logged_client_post(creator, "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"])
    )
    canceled_request = logged_client_post(creator, "get",
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"
