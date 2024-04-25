import json

from oarepo import __version__ as oarepo_version

is_oarepo_11 = oarepo_version.split(".")[0] == "11"

# RDM 12 adds "delete" to allowed actions (to be able to delete the request)
allowed_actions = ["submit"] if is_oarepo_11 else ["submit", "delete"]


def test_draft_publish_request_present(
    app, logged_client, users, record_ui_resource, example_topic_draft, fake_manifest
):
    with logged_client(users[0]).get(f"/thesis/{example_topic_draft['id']}/edit") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert data["creatable_request_types"]["thesis_publish_draft"] == {
            "description": "Request publishing of a draft",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{example_topic_draft['id']}/draft/requests/thesis_publish_draft"
                }
            },
            "name": "Publish draft",
        }


def test_draft_publish_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert "publish_draft" not in data["creatable_request_types"]


def test_record_delete_request_present(
    app, logged_client, users, record_ui_resource, example_topic, fake_manifest
):
    with logged_client(users[0]).get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert len(data["creatable_request_types"]) == 2
        assert data["creatable_request_types"]["thesis_edit_record"] == {
            "description": "Request re-opening of published record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{example_topic['id']}/requests/thesis_edit_record"
                }
            },
            "name": "Edit record",
        }
        assert data["creatable_request_types"]["thesis_delete_record"] == {
            "description": "Request deletion of published record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{example_topic['id']}/requests/thesis_delete_record"
                }
            },
            "name": "Delete record",
        }


def test_record_delete_unauthorized(
    app, record_ui_resource, example_topic, client, fake_manifest
):
    with client.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert "delete_record" not in data["creatable_request_types"]
