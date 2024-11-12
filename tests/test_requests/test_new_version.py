from thesis.records.api import ThesisDraft, ThesisRecord

from tests.test_requests.utils import link_api2testclient


def test_new_version_autoaccept(
    vocab_cf,
    logged_client,
    users,
    urls,
    new_version_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)

    new_version_direct = creator_client.post(
        f"{urls['BASE_URL']}{record1['id']}/versions",
    )
    assert new_version_direct.status_code == 403

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]
    assert "topic_redirect_link" in request["links"]["type_specific"]

    assert "draft_record:links:self" in request["payload"]
    assert "draft_record:links:self_html" in request["payload"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    # new_version action worked?
    search = creator_client.get(
        f'user{urls["BASE_URL"]}',
    ).json[
        "hits"
    ]["hits"]
    assert len(search) == 2
    assert search[0]["id"] != search[1]["id"]
    assert search[0]["parent"]["id"] == search[1]["parent"]["id"]
