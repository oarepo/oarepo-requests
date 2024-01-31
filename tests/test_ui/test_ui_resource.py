import json
from oarepo import __version__ as oarepo_version
is_oarepo_11 = oarepo_version.split(".")[0] == "11"

# RDM 12 adds "delete" to allowed actions (to be able to delete the request)
allowed_actions = ["submit"] if is_oarepo_11 else ["submit", "delete"]


def test_draft_publish_request_present(
    app, record_ui_resource, example_topic_draft, client_with_login, fake_manifest
):
    with client_with_login.get(f"/thesis/{example_topic_draft['id']}/edit") as c:
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
        data = json.loads(c.text)
        assert "delete_record" in data
        assert data["delete_record"]['type'] == "delete_record"
        assert data["delete_record"]["receiver"] is None
        assert data["delete_record"]["status"] == "created"
        assert data["delete_record"]["actions"] == allowed_actions


def test_record_delete_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "delete_record" not in c.text
