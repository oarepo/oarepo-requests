def test_conditional_receiver_creator_matches(
    logged_client,
    users,
    urls,
    conditional_recipient_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    # user[0] is creator, user[1] is receiver
    # user[0] is not a creator, user[2] is receiver

    creator = users[0]
    assert creator.id == "1"

    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="with_ct")

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=conditional_recipient_request_data_function(draft1.json["id"]),
    )

    assert resp_request_create.status_code == 201
    assert resp_request_create.json["receiver"] == {"user": "2"}


def test_conditional_receiver_creator_does_not_match(
    logged_client,
    users,
    urls,
    conditional_recipient_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    # user[0] is creator, user[1] is receiver
    # user[0] is not a creator, user[2] is receiver

    creator = users[1]
    assert creator.id != 1

    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="with_ct")

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=conditional_recipient_request_data_function(draft1.json["id"]),
    )

    assert resp_request_create.status_code == 201
    assert resp_request_create.json["receiver"] == {"user": "3"}
