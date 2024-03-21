from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_publish(
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
    draft3 = logged_client_request(creator, "post", urls["BASE_URL"], json={})
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = logged_client_request(creator, "get", f"/user{urls['BASE_URL']}")
    lst = logged_client_request(creator, "get", urls["BASE_URL"])
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 0

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
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft1.json['id']}/draft"
    )
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = logged_client_request(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"]),
    )
    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft2.json['id']}/draft"
    )
    assert "publish_draft" not in record.json["parent"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = logged_client_request(creator, "get", f"/user{urls['BASE_URL']}")
    lst = logged_client_request(creator, "get", urls["BASE_URL"])
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 1

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft2.json['id']}/draft"
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
    record = logged_client_request(
        receiver, "get", f"{urls['BASE_URL']}{draft2.json['id']}/draft"
    )

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft3.json["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = logged_client_request(
        creator, "get", f"{urls['BASE_URL']}{draft3.json['id']}/draft"
    )
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
