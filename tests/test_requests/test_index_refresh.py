from tests.test_requests.utils import link_api2testclient


def test_search(
    logged_client,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = creator_client.post(urls["BASE_URL"], json={})

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    # should work without refreshing requests index
    requests_search = creator_client.get(urls["BASE_URL_REQUESTS"]).json

    assert len(requests_search["hits"]["hits"]) == 1

    link = link_api2testclient(requests_search["hits"]["hits"][0]["links"]["self"])
    extended_link = link.replace("/requests/", "/requests/extended/")

    update = creator_client.put(
        extended_link,
        json={"title": "tralala"},
    )

    requests_search = creator_client.get(urls["BASE_URL_REQUESTS"]).json
    assert requests_search["hits"]["hits"][0]["title"] == "tralala"
