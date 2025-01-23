from oarepo_requests.notifications.builders.publish import PublishDraftRequestAcceptNotificationBuilder

def get_request_type(request_types_json, request_type):
    selected_entry = [
        entry for entry in request_types_json if entry["type_id"] == request_type
    ]
    if not selected_entry:
        return None
    return selected_entry[0]


def test_publish_accept_notification(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""

    original_builder = PublishDraftRequestAcceptNotificationBuilder
    # mock build to observe calls
    # mock_build = replace_notification_builder(original_builder)
    # assert not mock_build.called

    # inviter(curator.id, open_review_community.id, "curator")

    mail = app.extensions.get("mail")
    assert mail

    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft1["id"], "publish_draft"
    )

    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1['id']}/draft?expand=true"
    )

    with mail.record_messages() as outbox:
        # Validate that email was sent
        publish = receiver_client.post(
            link2testclient(
                record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
            ),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        print()