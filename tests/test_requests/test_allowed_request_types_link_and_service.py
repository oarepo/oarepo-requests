#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from flask import current_app
from thesis.ext import ThesisExt
from thesis.records.api import ThesisDraft, ThesisRecord

from tests.test_requests.utils import link2testclient


def test_allowed_request_types_on_draft_service(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)

    thesis_ext: ThesisExt = current_app.extensions["thesis"]
    thesis_requests_service = thesis_ext.service_record_request_types

    allowed_request_types = (
        thesis_requests_service.get_applicable_request_types_for_draft_record(
            creator.identity, draft1.json["id"]
        )
    )
    assert sorted(
        allowed_request_types.to_dict()["hits"]["hits"], key=lambda x: x["type_id"]
    ) == [
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/delete_draft'
                }
            },
            "type_id": "delete_draft",
        },
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'
                }
            },
            "type_id": "publish_draft",
        },
    ]


def test_allowed_request_types_on_draft_resource(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)

    applicable_requests_link = draft1.json["links"]["applicable-requests"]
    assert (
        applicable_requests_link
        == f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/applicable'
    )
    allowed_request_types = creator_client.get(
        link2testclient(applicable_requests_link)
    )
    assert sorted(
        allowed_request_types.json["hits"]["hits"], key=lambda x: x["type_id"]
    ) == [
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/delete_draft'
                }
            },
            "type_id": "delete_draft",
        },
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'
                }
            },
            "type_id": "publish_draft",
        },
    ]


def publish_record(
    creator_client, urls, publish_request_data_function, draft1, receiver_client
):
    id_ = draft1.json["id"]
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = receiver_client.get(
        f"{urls['BASE_URL']}{id_}/draft?expand=true"
    )

    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    return creator_client.get(f"{urls['BASE_URL']}{id_}?expand=true").json


def test_allowed_request_types_on_published_resource(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
    app,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    published1 = publish_record(
        creator_client, urls, publish_request_data_function, draft1, receiver_client
    )

    applicable_requests_link = published1["links"]["applicable-requests"]
    assert (
        applicable_requests_link
        == f'https://127.0.0.1:5000/api/thesis/{published1["id"]}/requests/applicable'
    )
    allowed_request_types = creator_client.get(
        link2testclient(applicable_requests_link)
    )
    assert allowed_request_types.status_code == 200
    assert sorted(
        allowed_request_types.json["hits"]["hits"], key=lambda x: x["type_id"]
    ) == [
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{published1["id"]}/requests/delete_published_record'
                }
            },
            "type_id": "delete_published_record",
        },
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{published1["id"]}/requests/edit_published_record'
                }
            },
            "type_id": "edit_published_record",
        },
        {
            "links": {
                "actions": {
                    "create": f'https://127.0.0.1:5000/api/thesis/{published1["id"]}/requests/new_version'
                }
            },
            "type_id": "new_version",
        },
    ]


def test_ui_serialization(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    record_factory,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)

    draft_to_publish = create_draft_via_resource(creator_client)
    published1 = publish_record(
        creator_client,
        urls,
        publish_request_data_function,
        draft_to_publish,
        receiver_client,
    )
    draft_id = draft1.json["id"]
    published_id = published1["id"]

    applicable_requests_link_draft = draft1.json["links"]["applicable-requests"]
    applicable_requests_link_published = published1["links"]["applicable-requests"]

    allowed_request_types_draft = creator_client.get(
        link2testclient(applicable_requests_link_draft),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    allowed_request_types_published = creator_client.get(
        link2testclient(applicable_requests_link_published),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    sorted_draft_list = allowed_request_types_draft.json["hits"]["hits"]
    sorted_draft_list.sort(key=lambda serialized_rt: serialized_rt["type_id"])

    assert sorted_draft_list == [
        {
            "dangerous": True,
            "description": "Request deletion of draft",
            "editable": False,
            "has_form": False,
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{draft_id}/draft/requests/delete_draft"
                }
            },
            "name": "Delete draft",
            "stateful_description": "Click to permanently delete the draft.",
            "stateful_name": "Delete draft",
            "type_id": "delete_draft",
        },
        {
            "description": "Request publishing of a draft",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{draft_id}/draft/requests/publish_draft"
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
                    "create": f"https://127.0.0.1:5000/api/thesis/{published_id}/requests/delete_published_record"
                }
            },
            "description": "Request deletion of published record",
            "name": "Delete record",
            "dangerous": True,
            "editable": False,
            "has_form": False,
            "stateful_description": "Request permission to delete the record.",
            "stateful_name": "Request record deletion",
        },
        {
            "type_id": "edit_published_record",
            "links": {
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{published_id}/requests/edit_published_record"
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
                "actions": {
                    "create": f"https://127.0.0.1:5000/api/thesis/{published_id}/requests/new_version"
                }
            },
            "description": "Request requesting creation of new version of a published record.",
            "name": "New Version",
            "dangerous": False,
            "editable": False,
            "has_form": True,
            "stateful_description": "Click to start creating a new version of the "
            "record.",
            "stateful_name": "New Version",
        },
    ]
