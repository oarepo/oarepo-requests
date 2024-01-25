

def test_read_extended(client_factory, identity_simple, users, urls, publish_request_data_function):
    creator_client = users[0].login(client_factory())
    receiver = users[1]

    draft1 = creator_client.post(urls['BASE_URL'], json={})
    resp_request_create = creator_client.post(
        urls['BASE_URL_REQUESTS'], json=publish_request_data_function(receiver, draft1)
    )

    old_call = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_create.json['id']}")
    new_call = creator_client.get(f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}")
    new_call2 = creator_client.get(f"{urls['BASE_URL_REQUESTS']}extended/{resp_request_create.json['id']}",
                                   headers={"Accept":"application/vnd.inveniordm.v1+json"})
    #new_call3 = creator_client.get(f"{BASE_URL_REQUESTS}extended/{resp_request_create.json['id']}",
    #                               headers={"Content-Type":"svdfvgfdgf"})
    print()
