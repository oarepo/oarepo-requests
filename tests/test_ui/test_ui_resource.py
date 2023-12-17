import json


def test_draft_publish_request_present(
    app, record_ui_resource, example_topic_draft, client_with_login, fake_manifest
):
    def check_request(ctext):
        assert "publish_draft:" in ctext
        assert "type&#39;: &#39;publish_draft&#39;" in ctext
        assert "&#39;status&#39;: &#39;created&#39;" in ctext
        assert "&#39;receiver&#39;: None" in ctext
        assert "&#39;actions&#39;: [&#39;submit&#39;]" in ctext

    with client_with_login.get(f"/thesis/{example_topic_draft['id']}/edit") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert data["available_requests"]["publish_draft"] == {'actions': ['submit', 'delete'], 'receiver': None, 'status': 'created', 'type': 'publish_draft'}
        assert data["form_config"]["publish_draft"] == {'actions': ['submit', 'delete'], 'receiver': None, 'status': 'created', 'type': 'publish_draft'}


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
        data = json.loads(c.text)
        assert "delete_record" in data
        assert data["delete_record"]['type'] == "delete_record"
        assert data["delete_record"]["receiver"] is None
        assert data["delete_record"]["status"] == "created"
        assert data["delete_record"]["actions"] == ["submit", "delete"]


def test_record_delete_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "delete_record" not in c.text
