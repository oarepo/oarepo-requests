from thesis.records.api import ThesisDraft, ThesisRecord

from tests.test_requests.utils import link_api2testclient


def test_edit_autoaccept(
    logged_client_request,
    identity_simple,
    users,
    urls,
    edit_record_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    record1 = record_factory()

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=edit_record_data_function(record1["id"]),
    )
    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = logged_client_request(
        creator,
        "get",
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    # edit action worked?
    search = logged_client_request(
        creator,
        "get",
        f'user{urls["BASE_URL"]}',
    ).json[
        "hits"
    ]["hits"]
    assert len(search) == 1
    assert search[0]["links"]["self"].endswith("/draft")
