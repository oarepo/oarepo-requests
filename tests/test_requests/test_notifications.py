from oarepo_requests.notifications.builders.publish import PublishDraftRequestAcceptNotificationBuilder
from .test_create_inmodel import pick_request_type
from .utils import link2testclient


def test_publish_accept_notification(
    app,
    users,
    logged_client,
    create_draft_via_resource,
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

    draft1 = create_draft_via_resource(creator_client)
    link = link2testclient(
        pick_request_type(draft1.json["expanded"]["request_types"], "publish_draft")[
            "links"
        ]["actions"]["create"]
    )
    resp_request_create = creator_client.post(
        link, json={"payload": {"version": "1.0"}}
    )
    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )

    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
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