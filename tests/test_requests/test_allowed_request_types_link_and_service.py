from flask import current_app
from thesis.ext import ThesisExt
from thesis.records.api import ThesisDraft, ThesisRecord

from tests.test_requests.utils import link_api2testclient


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
    thesis_requests_service = thesis_ext.service_requests

    allowed_request_types = (
        thesis_requests_service.get_applicable_request_types_for_draft(
            creator.identity, draft1.json["id"]
        )
    )
    assert allowed_request_types.to_dict() == {
        "hits": {
            "hits": [
                {
                    "links": {
                        "actions": {
                            "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'
                        }
                    },
                    "type_id": "publish_draft",
                }
            ],
            "total": 1,
        },
        "links": {
            "self": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/applicable'
        },
    }


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
        link_api2testclient(applicable_requests_link)
    )
    assert allowed_request_types.json == {
        "hits": {
            "hits": [
                {
                    "links": {
                        "actions": {
                            "create": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'
                        }
                    },
                    "type_id": "publish_draft",
                }
            ],
            "total": 1,
        },
        "links": {
            "self": f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/applicable'
        },
    }


def publish_record(
    creator_client, urls, publish_request_data_function, draft1, receiver_client
):
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    lst = creator_client.get(urls["BASE_URL"])
    return lst.json["hits"]["hits"][0]


def test_allowed_request_types_on_published_resource(
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
    published1 = publish_record(
        creator_client, urls, publish_request_data_function, draft1, receiver_client
    )

    applicable_requests_link = published1["links"]["applicable-requests"]
    assert (
        applicable_requests_link
        == f'https://127.0.0.1:5000/api/thesis/{published1["id"]}/requests/applicable'
    )
    allowed_request_types = creator_client.get(
        link_api2testclient(applicable_requests_link)
    )
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
