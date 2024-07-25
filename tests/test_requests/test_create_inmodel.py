from thesis.records.api import ThesisRecord

from tests.test_requests.utils import link_api2testclient


def pick_request_type(types_list, queried_type):
    for type in types_list:
        if type["type_id"] == queried_type:
            return type
    return None


def test_record(
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
    record1 = creator_client.get(f"{urls['BASE_URL']}{record1['id']}?expand=true")

    link = link_api2testclient(
        pick_request_type(
            record1.json["expanded"]["request_types"], "delete_published_record"
        )["links"]["actions"]["create"]
    )

    resp_request_create = creator_client.post(link)
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    record = receiver_client.get(f"{urls['BASE_URL']}{record1.json['id']}?expand=true")
    delete = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )
    ThesisRecord.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 0


def test_draft(
    vocab_cf,
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
    link = link_api2testclient(
        pick_request_type(draft1.json["expanded"]["request_types"], "publish_draft")[
            "links"
        ]["actions"]["create"]
    )

    resp_request_create = creator_client.post(link)
    assert resp_request_create.status_code == 201
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    delete = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        )
    )
    ThesisRecord.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    assert len(lst.json["hits"]["hits"]) == 1
