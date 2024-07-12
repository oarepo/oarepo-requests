from tests.test_requests.test_create_inmodel import pick_request_type
from tests.test_requests.utils import link_api2testclient


def test_requests_field(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = creator_client.post(urls["BASE_URL"] + "?expand=true", json={})
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
    record = receiver_client.get(f"{urls['BASE_URL']}{draft1.json['id']}/draft")
    expanded_record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )

    assert "requests" not in record.json.get("expanded", {})
    assert "requests" in expanded_record.json["expanded"]
