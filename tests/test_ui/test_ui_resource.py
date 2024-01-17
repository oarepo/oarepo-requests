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
