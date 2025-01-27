def test_publish_notifications(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""

    mail = app.extensions.get("mail")
    assert mail

    creator = users[0]
    receiver = users[1]
    receiver_client = logged_client(receiver)
    draft1 = draft_factory(creator.identity)

    with mail.record_messages() as outbox:
        resp_request_submit = submit_request_on_draft(
            creator.identity, draft1["id"], "publish_draft"
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]

    record = receiver_client.get(f"{urls['BASE_URL']}{draft1['id']}/draft?expand=true")

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


def test_delete_published_notifications(
    app,
    users,
    logged_client,
    record_factory,
    submit_request_on_record,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""

    mail = app.extensions.get("mail")
    assert mail

    creator = users[0]
    receiver = users[1]
    receiver_client = logged_client(receiver)
    record1 = record_factory(creator.identity)

    with mail.record_messages() as outbox:
        resp_request_submit = submit_request_on_record(
            creator.identity, record1["id"], "delete_published_record"
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]

    record = receiver_client.get(f"{urls['BASE_URL']}{record1['id']}?expand=true")

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


def test_group(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    add_user_in_role,
    role,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""

    mail = app.extensions.get("mail")
    config_restore = app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]
    add_user_in_role(users[0], role)
    add_user_in_role(users[1], role)

    def current_receiver(record=None, request_type=None, **kwargs):
        if request_type.type_id == "publish_draft":
            return role
        return config_restore(record, request_type, **kwargs)

    try:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = current_receiver

        creator = users[0]
        draft1 = draft_factory(creator.identity)

        with mail.record_messages() as outbox:
            submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
            assert len(outbox) == 2
            receivers = {m.recipients[0] for m in outbox}
            assert receivers == {"user1@example.org", "user2@example.org"}

    finally:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = config_restore
