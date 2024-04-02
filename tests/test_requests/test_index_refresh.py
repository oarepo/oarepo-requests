from tests.test_requests.utils import link_api2testclient


def test_search(
    logged_client_request,
    identity_simple,
    users,
    urls,
    publish_request_data_function,
    search_clear,
):
    creator = users[0]

    draft1 = logged_client_request(creator, "post", urls["BASE_URL"], json={})

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    # should work without refreshing requests index
    requests_search = logged_client_request(
        creator, "get", urls["BASE_URL_REQUESTS"]
    ).json

    assert len(requests_search["hits"]["hits"]) == 1

    link = link_api2testclient(requests_search["hits"]["hits"][0]["links"]["self"])
    extended_link = link.replace("/requests/", "/requests/extended/")

    update = logged_client_request(
        creator,
        "put",
        extended_link,
        json={"title": "tralala"},
    )

    requests_search = logged_client_request(
        creator, "get", urls["BASE_URL_REQUESTS"]
    ).json

    assert requests_search["hits"]["hits"][0]["title"] == "tralala"
