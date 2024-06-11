from tests.test_requests.test_create_inmodel import pick_request_type
from tests.test_requests.utils import link_api2testclient
from invenio_requests.records.api import RequestEvent


def test_timeline(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    link = link_api2testclient(
        pick_request_type(draft1.json["request_types"], "thesis_publish_draft")[
            "links"
        ]["actions"]["create"]
    )

    publish_request_resp = creator_client.post(link)
    assert publish_request_resp.status_code == 201

    publish_request_submit_resp = creator_client.post(
        link_api2testclient(publish_request_resp.json["links"]["actions"]["submit"]),
    )
    assert publish_request_submit_resp.status_code == 200

    comment_resp = creator_client.post(
        link_api2testclient(publish_request_resp.json["links"]["comments"]),
        json={"payload": {"content": "test"}},
    )
    assert comment_resp.status_code == 201
    RequestEvent.index.refresh()

    timeline_resp = creator_client.get(
        link_api2testclient(publish_request_resp.json["links"]["timeline"]),
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1

    # vnd serialization
    timeline_resp = creator_client.get(
        link_api2testclient(publish_request_resp.json["links"]["timeline"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json["hits"]["hits"]) == 1