#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_access.permissions import system_identity


def test_resolve_topic(
    db,
    requests_model,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_on_record,
    record_service,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    logged_client(receiver)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record1_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    assert resp_request_submit["status"] == "submitted"

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    assert resp.json["expanded"][
        "topic"
    ] == {  # TODO: why is there a test creators and contributors in metadata?
        "id": record1_id,
        "metadata": {
            "contributors": ["Contributor 1"],
            "creators": ["Creator 1", "Creator 2"],
            "title": "blabla",
        },
        "links": {
            "latest_html": f"https://127.0.0.1:5000/api/test-ui-links/latest/{record1_id}",
            "self": f"https://127.0.0.1:5000/api/requests-test/{record1_id}",
            "self_html": f"https://127.0.0.1:5000/api/test-ui-links/detail/{record1_id}",
        },
    }

    record_service.delete(system_identity, record1_id)
    requests_model.Record.index.refresh()

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {"requests_test": record1_id}

    resp_expanded = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp_expanded.status_code == 200
    assert resp_expanded.json["topic"] == {"requests_test": record1_id}
    assert resp_expanded.json["expanded"]["topic"] == {
        "id": "",  # TODO: ask - should id be shown?
        "links": {},
        "metadata": {"title": "Deleted record"},
    }


"""
def test_ui_resolve_topic(
    db,
    requests_model,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_on_record,
    record_service,
    link2testclient,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    logged_client(receiver)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    resp_request_submit = submit_request_on_record(
        creator.identity,
        record1_id,
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    assert resp_request_submit["status"] == "submitted"

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    assert (
        resp.json["topic"].items()
        >= {
            "reference": {"test_requests": record1_id},
            "type": "test_requests",
            "label": "blabla",
        }.items()
    )
    assert (
        resp.json["topic"]["links"].items()
        >= {
            "self": f"https://127.0.0.1:5000/api/requests-test/{record1_id}",
            "self_html": f"https://127.0.0.1:5000/requests-test/{record1_id}",
        }.items()
    )
    assert resp.json["stateful_name"] == "Record deletion requested"
    assert resp.json["stateful_description"] == (
        "Permission to delete record requested. You will be notified about the decision by email."
    )

    record_service.delete(system_identity, record1_id)
    requests_model.Record.index.refresh()

    resp = creator_client.get(
        link2testclient(resp_request_submit["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {
        "reference": {
            "test_requests": record1_id,
        },
        "status": "deleted",
    }
    assert resp.json["stateful_name"] == "Delete record"
    assert resp.json["stateful_description"] == "Request deletion of published record"
"""
