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
        data = json.loads(c.text)
        assert data["creatable_request_types"]["non_duplicable"] == {
            "description": "",
            "links": {"actions": {"create": "https://127.0.0.1:5000/api/requests"}},
            "name": "Non-duplicable",
        }
        assert data["creatable_request_types"]["publish_draft"] == {
            "description": "request publishing of a draft",
            "links": {"actions": {"create": "https://127.0.0.1:5000/api/requests"}},
            "name": "Publish-draft",
        }


def test_draft_publish_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert "publish_draft" not in data["creatable_request_types"]


def test_record_delete_request_present(
    app, record_ui_resource, example_topic, client_with_login, fake_manifest
):
    with client_with_login.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert len(data["creatable_request_types"]) == 2
        assert data["creatable_request_types"]["generic_request"] == {
            "description": "",
            "links": {"actions": {"create": "https://127.0.0.1:5000/api/requests"}},
            "name": "Generic-request",
        }
        assert data["creatable_request_types"]["delete_record"] == {
            "description": "request deletion of published record",
            "links": {"actions": {"create": "https://127.0.0.1:5000/api/requests"}},
            "name": "Delete-record",
        }


def test_record_delete_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert "delete_record" not in data["creatable_request_types"]
