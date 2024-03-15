from thesis.records.api import ThesisRecord

from tests.test_requests.utils import link_api2testclient


def pick_request_type(types_list, queried_type):
    for type in types_list:
        if type["type_id"] == queried_type:
            return type
    return None


def test_record(
    logged_client_post,
    record_factory,
    identity_simple,
    users,
    urls,
    delete_record_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    record1 = record_factory()
    record1 = logged_client_post(creator, "get", f"{urls['BASE_URL']}{record1['id']}")

    link = link_api2testclient(
        pick_request_type(record1.json["request_types"], "thesis_delete_record")[
            "links"
        ]["actions"]["create"]
    )

    resp_request_create = logged_client_post(
        creator,
        "post",
        link,
        json={"receiver": {"user": receiver.id}},
    )
    assert resp_request_create.status_code == 201
    resp_request_submit = logged_client_post(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    record = logged_client_post(
        receiver, "get", f"{urls['BASE_URL']}{record1.json['id']}"
    )
    delete = logged_client_post(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"]),
    )
    ThesisRecord.index.refresh()
    lst = logged_client_post(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 0


def test_draft(
    logged_client_post,
    identity_simple,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    draft1 = logged_client_post(creator, "post", urls["BASE_URL"], json={})
    link = link_api2testclient(
        pick_request_type(draft1.json["request_types"], "thesis_publish_draft")[
            "links"
        ]["actions"]["create"]
    )

    resp_request_create = logged_client_post(
        creator,
        "post",
        link,
        json={"receiver": {"user": receiver.id}},
    )
    assert resp_request_create.status_code == 201
    resp_request_submit = logged_client_post(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    record = logged_client_post(
        receiver, "get", f"{urls['BASE_URL']}{draft1.json['id']}/draft"
    )
    delete = logged_client_post(
        receiver,
        "post",
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"]),
    )
    ThesisRecord.index.refresh()
    lst = logged_client_post(creator, "get", urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 1
