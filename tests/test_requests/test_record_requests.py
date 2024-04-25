from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_read_requests_on_draft(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    draft2 = creator_client.post(urls["BASE_URL"], json={})
    draft3 = creator_client.post(urls["BASE_URL"], json={})
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    r1 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    r2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    r3 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )

    creator_client.get(link_api2testclient(r1.json["links"]["actions"]["submit"]))
    creator_client.get(link_api2testclient(r2.json["links"]["actions"]["submit"]))
    creator_client.get(link_api2testclient(r3.json["links"]["actions"]["submit"]))

    resp1 = creator_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft/requests"
    ).json["hits"]["hits"]
    resp2 = creator_client.get(
        f"{urls['BASE_URL']}{draft2.json['id']}/draft/requests"
    ).json["hits"]["hits"]
    resp3 = creator_client.get(
        f"{urls['BASE_URL']}{draft3.json['id']}/draft/requests"
    ).json["hits"]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0

    # todo test permissions?


def test_read_requests_on_record(
    logged_client,
    record_factory,
    users,
    urls,
    delete_record_data_function,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    record3 = record_factory(creator.identity)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    r1 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    r2 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    r3 = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record2["id"]),
    )

    creator_client.post(link_api2testclient(r1.json["links"]["actions"]["submit"]))
    creator_client.post(link_api2testclient(r2.json["links"]["actions"]["submit"]))
    creator_client.post(link_api2testclient(r3.json["links"]["actions"]["submit"]))

    resp1 = creator_client.get(f"{urls['BASE_URL']}{record1['id']}/requests").json[
        "hits"
    ]["hits"]
    resp2 = creator_client.get(f"{urls['BASE_URL']}{record2['id']}/requests").json[
        "hits"
    ]["hits"]
    resp3 = creator_client.get(f"{urls['BASE_URL']}{record3['id']}/requests").json[
        "hits"
    ]["hits"]

    assert len(resp1) == 2
    assert len(resp2) == 1
    assert len(resp3) == 0
