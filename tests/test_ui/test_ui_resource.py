import json

from invenio_requests.proxies import current_requests_service

from oarepo_requests.types import EditPublishedRecordRequestType

allowed_actions = ["submit", "delete"]


def test_draft_publish_request_present(
    app, logged_client, users, record_ui_resource, example_topic_draft, fake_manifest
):
    with logged_client(users[0]).get(f"/thesis/{example_topic_draft['id']}/edit") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        print(data)
        assert data["creatable_request_types"]["publish_draft"] == {
            "description": "Request publishing of a draft",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{example_topic_draft['id']}/draft/requests/publish_draft"
                }
            },
            "name": "Publish draft",
        }


def test_record_delete_request_present(
    app, record_ui_resource, logged_client, users, record_factory, fake_manifest
):
    topic = record_factory(users[0].identity)
    with logged_client(users[0]).get(f"/thesis/{topic['id']}") as c:
        assert c.status_code == 200
        print(c.text)
        data = json.loads(c.text)
        assert len(data["creatable_request_types"]) == 3
        assert data["creatable_request_types"]["edit_published_record"] == {
            "description": "Request re-opening of published record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{topic['id']}/requests/edit_published_record"
                }
            },
            "name": "Edit record",
        }
        assert data["creatable_request_types"]["delete_published_record"] == {
            "description": "Request deletion of published record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{topic['id']}/requests/delete_published_record"
                }
            },
            "name": "Delete record",
        }


def test_record_delete_unauthorized(
    app, record_ui_resource, users, record_factory, client, fake_manifest
):
    topic = record_factory(users[0].identity)
    with client.get(f"/thesis/{topic['id']}") as c:
        assert c.status_code == 200
        data = json.loads(c.text)
        assert "delete_record" not in data["creatable_request_types"]


def test_request_detail_page(
    app,
    logged_client,
    record_ui_resource,
    users,
    record_factory,
    client,
    fake_manifest,
    urls,
):
    topic = record_factory(users[0].identity)
    creator_client = logged_client(users[0])
    creator_identity = users[0].identity
    request = current_requests_service.create(
        creator_identity,
        {},
        EditPublishedRecordRequestType,
        topic=topic,
        receiver=users[1].user,
        creator=users[0].user,
    )
    # resp_request_submit = creator_client.post(
    #     link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    # )
    request_id = request["id"]

    with creator_client.get(f"/requests/{request_id}") as c:
        assert c.status_code == 200
        print(c.text)


def test_form_config(app, client, record_ui_resource, fake_manifest):
    with client.get("/requests/configs/publish_draft") as c:
        assert c.json == {
            "allowedHtmlAttrs": {
                "*": ["class"],
                "a": ["href", "title", "name", "class", "rel"],
                "abbr": ["title"],
                "acronym": ["title"],
            },
            "allowedHtmlTags": [
                "a",
                "abbr",
                "acronym",
                "b",
                "blockquote",
                "br",
                "code",
                "div",
                "table",
                "tbody",
                "td",
                "th",
                "tr",
                "em",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "i",
                "li",
                "ol",
                "p",
                "pre",
                "span",
                "strike",
                "strong",
                "sub",
                "sup",
                "u",
                "ul",
            ],
            "custom_fields": {
                "ui": [
                    {
                        "section": "",
                        "fields": [
                            {
                                "field": "version",
                                "props": {
                                    "label": "Resource version",
                                    "placeholder": "Write down the version (first, second…).",
                                    "required": False,
                                },
                                "ui_widget": "Input",
                            }
                        ],
                    }
                ]
            },
            "request_type_properties": {
                "dangerous": False,
                "editable": False,
                "has_form": True,
            },
            "action_labels": {
                {
                    "accept": "Publish",
                    "cancel": "Cancel",
                    "create": "Create",
                    "decline": "Return for correction",
                    "delete": "Delete",
                    "expire": "Expire",
                    "submit": "Submit",
                }
            },
        }
