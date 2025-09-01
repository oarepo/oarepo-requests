#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from flask import current_app
from pytest_oarepo.functions import clear_babel_context


# def test_workflow_read(workflow_model, users, logged_client, default_workflow_json, location, search_clear):
def test_allowed_request_types_on_draft_service(
    requests_model,
    users,
    draft_factory,
    search_clear,
):
    identity = users[0].identity

    draft1 = draft_factory(identity)
    draft1_id = draft1["id"]

    test_ext = current_app.extensions["requests_test"]
    test_requests_service = test_ext.service_record_request_types

    allowed_request_types = test_requests_service.get_applicable_request_types_for_draft_record(identity, draft1_id)
    assert sorted(allowed_request_types.to_dict()["hits"]["hits"], key=lambda x: x["type_id"]) == [
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft1_id}/draft/requests/delete_draft"
                }
            },
            "type_id": "delete_draft",
        },
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft1_id}/draft/requests/publish_draft"
                }
            },
            "type_id": "publish_draft",
        },
    ]


def test_allowed_request_types_on_draft_resource(
    requests_model,
    logged_client,
    users,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]

    applicable_requests_link = draft1["links"]["applicable-requests"]
    assert applicable_requests_link == f"https://127.0.0.1:5000/api/requests-test/{draft1_id}/draft/requests/applicable"
    allowed_request_types = creator_client.get(link2testclient(applicable_requests_link))
    assert sorted(allowed_request_types.json["hits"]["hits"], key=lambda x: x["type_id"]) == [
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft1_id}/draft/requests/delete_draft"
                }
            },
            "type_id": "delete_draft",
        },
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft1_id}/draft/requests/publish_draft"
                }
            },
            "type_id": "publish_draft",
        },
    ]


def test_allowed_request_types_on_published_resource(
    requests_model,
    logged_client,
    users,
    record_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)

    published1 = record_factory(creator.identity)
    published1_id = published1["id"]

    applicable_requests_link = published1["links"]["applicable-requests"]
    assert applicable_requests_link == f"https://127.0.0.1:5000/api/requests-test/{published1_id}/requests/applicable"
    allowed_request_types = creator_client.get(link2testclient(applicable_requests_link))
    assert allowed_request_types.status_code == 200
    assert sorted(allowed_request_types.json["hits"]["hits"], key=lambda x: x["type_id"]) == [
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{published1_id}/requests/delete_published_record"
                }
            },
            "type_id": "delete_published_record",
        },
        {
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{published1_id}/requests/edit_published_record"
                }
            },
            "type_id": "edit_published_record",
        },
        {
            "links": {
                "actions": {"create": f"https://127.0.0.1:5000/api/requests-test/{published1_id}/requests/new_version"}
            },
            "type_id": "new_version",
        },
    ]


def test_ui_serialization(
    logged_client,
    users,
    draft_factory,
    record_factory,
    link2testclient,
    app,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    published1 = record_factory(creator.identity)

    draft_id = draft1["id"]
    published_id = published1["id"]

    applicable_requests_link_draft = draft1["links"]["applicable-requests"]
    applicable_requests_link_published = published1["links"]["applicable-requests"]

    # with app.test_request_context(headers=[("Accept-Language", "en")]):
    allowed_request_types_draft = creator_client.get(
        link2testclient(applicable_requests_link_draft), headers={"Accept": "application/vnd.inveniordm.v1+json"}
    )

    allowed_request_types_published = creator_client.get(
        link2testclient(applicable_requests_link_published), headers={"Accept": "application/vnd.inveniordm.v1+json"}
    )

    sorted_draft_list = allowed_request_types_draft.json["hits"]["hits"]
    sorted_draft_list.sort(key=lambda serialized_rt: serialized_rt["type_id"])
    print(sorted_draft_list)
    assert sorted_draft_list == [
        {
            "dangerous": True,
            "description": "Request deletion of draft",
            "editable": False,
            "has_form": False,
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft_id}/draft/requests/delete_draft"
                }
            },
            "name": "Delete draft",
            "stateful_description": "Click to permanently delete the draft.",
            "stateful_name": "Delete draft",
            "type_id": "delete_draft",
        },
        {
            "description": "Request to publish a draft",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{draft_id}/draft/requests/publish_draft"
                }
            },
            "name": "Publish draft",
            "type_id": "publish_draft",
            "dangerous": False,
            "editable": False,
            "has_form": True,
            "stateful_description": "By submitting the draft for review you are "
            "requesting the publication of the draft. The draft "
            "will become locked and no further changes will be "
            "possible until the request is accepted or declined. "
            "You will be notified about the decision by email.",
            "stateful_name": "Submit for review",
        },
    ]
    sorted_published_list = allowed_request_types_published.json["hits"]["hits"]
    sorted_published_list.sort(key=lambda serialized_rt: serialized_rt["type_id"])
    assert sorted_published_list == [
        {
            "type_id": "delete_published_record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{published_id}/requests/delete_published_record"
                }
            },
            "description": "Request deletion of published record",
            "name": "Delete record",
            "dangerous": True,
            "editable": False,
            "has_form": True,  # now there is form for record delete
            "stateful_description": "Request permission to delete the record.",
            "stateful_name": "Request record deletion",
        },
        {
            "type_id": "edit_published_record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/requests-test/{published_id}/requests/edit_published_record"
                }
            },
            "description": "Request re-opening of published record",
            "name": "Edit metadata",
            "dangerous": False,
            "editable": False,
            "has_form": False,
            "stateful_description": "Click to start editing the metadata of the record.",
            "stateful_name": "Edit metadata",
        },
        {
            "type_id": "new_version",
            "links": {
                "actions": {"create": f"https://127.0.0.1:5000/api/requests-test/{published_id}/requests/new_version"}
            },
            "description": "Request requesting creation of new version of a published record.",
            "name": "New Version",
            "dangerous": False,
            "editable": False,
            "has_form": True,
            "stateful_description": "Click to start creating a new version of the record.",
            "stateful_name": "New Version",
        },
    ]
