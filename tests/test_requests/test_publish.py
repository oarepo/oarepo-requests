from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_publish(client_factory, identity_simple, users, urls, publish_request_data_function):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    draft1 = creator_client.post(urls['BASE_URL'], json={})
    draft2 = creator_client.post(urls['BASE_URL'], json={})
    draft3 = creator_client.post(urls['BASE_URL'], json={})
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls['BASE_URL'])
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 0

    resp_request_create = creator_client.post(
        urls['BASE_URL_REQUESTS'], json=publish_request_data_function(receiver, draft1)
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"])
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{draft2.json['id']}/draft")
    assert "publish_draft" not in record.json["parent"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls['BASE_URL'])
    assert len(draft_lst.json["hits"]["hits"]) == 2
    assert len(lst.json["hits"]["hits"]) == 1

    resp_request_create = creator_client.post(
        urls['BASE_URL_REQUESTS'], json=publish_request_data_function(receiver, draft2)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{draft2.json['id']}/draft")
    decline = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["decline"])
    )
    declined_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"
    record = receiver_client.get(f"{urls['BASE_URL']}{draft2.json['id']}/draft")

    resp_request_create = creator_client.post(
        urls['BASE_URL_REQUESTS'], json=publish_request_data_function(receiver, draft3)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = creator_client.get(f"{urls['BASE_URL']}{draft3.json['id']}/draft")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = creator_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"])
    )
    canceled_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"
