
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

    ThesisRecord.index.refresh()



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
    draft_id = draft1.json["id"]

    resp_request_create = logged_client_post(
        creator,
        "post",
        f"{urls['BASE_URL']}{draft_id}/draft/requests/thesis_draft_publish_draft",
        json={"receiver":{"user": receiver.id}},
    )
    assert resp_request_create.status_code == 201
    assert resp_request_create.json.request_types
    print()

