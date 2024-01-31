from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request

from oarepo_requests.proxies import current_oarepo_requests


def data(receiver, record_id):
    return {
        "receiver": {"user": receiver.id},
        "request_type": "publish_draft",
        "topic": {"thesis_draft": record_id},
    }


def test_draft_publish_request_present(
    app, record_ui_resource, example_topic_draft, client_logged_as, users, fake_manifest
):
    def check_request(ctext):
        assert "publish_draft:" in ctext
        assert "type&#39;: &#39;publish_draft&#39;" in ctext
        assert "&#39;status&#39;: &#39;created&#39;" in ctext
        assert "&#39;receiver&#39;: None" in ctext
        assert "&#39;actions&#39;: [&#39;submit&#39;]" in ctext

    user = users[0]
    logged_client = client_logged_as(user.email)
    with logged_client.get(f"/thesis/{example_topic_draft['id']}/edit") as c:
        assert c.status_code == 200
        base_part, form_part = c.text.split("allowed requests in form config:")
        check_request(base_part)
        check_request(form_part)


def test_ui_serialization(
    app, record_ui_resource, users, client_logged_as, example_topic_draft, fake_manifest
):
    creator = users[0]
    receiver = users[1]
    creator_client = client_logged_as(creator.email)
    receiver_client = client_logged_as(receiver.email)

    oarepo_requests_service = current_oarepo_requests.requests_service

    request = oarepo_requests_service.create(
        creator.identity,
        {},
        "publish_draft",
        receiver={"user": "2"},
        creator={"user": "1"},
        topic={"thesis_draft": str(example_topic_draft["id"])},
    )
    submit_resp = current_requests_service.execute_action(
        creator.identity, request.id, "submit"
    )
    Request.index.refresh()

    """
    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, example_topic_draft.id)
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    """

    with receiver_client.get(f"/thesis/{example_topic_draft['id']}/edit") as c:
        assert c.status_code == 200
        assert "created_by" in c.text
        print()


def test_draft_publish_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "publish_draft" not in c.text


def test_record_delete_request_present(
    app, record_ui_resource, example_topic, client_with_login, fake_manifest
):
    with client_with_login.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "delete_record: " in c.text
        assert "&#39;type&#39;: &#39;delete_record&#39" in c.text
        assert "&#39;receiver&#39;: None" in c.text
        assert "&#39;status&#39;: &#39;created&#39;" in c.text
        assert "&#39;links&#39;: {}" in c.text
        assert "&#39;actions&#39;: [&#39;submit&#39;]" in c.text


def test_record_delete_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "delete_record" not in c.text
