#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import json

from invenio_access.permissions import system_identity
from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient


def test_resolve_topic(
    db,
    vocab_cf,
    logged_client,
    record_factory,
    users,
    urls,
    delete_record_data_function,
    record_service,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    assert resp_request_submit.json["status"] == "submitted"

    resp = creator_client.get(
        link_api2testclient(resp_request_create.json["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    assert resp.json["expanded"]["topic"] == {
        "id": record1["id"],
        "metadata": {
            "contributors": ["Contributor 1"],
            "creators": ["Creator 1", "Creator 2"],
            "title": "blabla",
        },
    }

    record_service.delete(system_identity, record1["id"])
    ThesisRecord.index.refresh()

    resp = creator_client.get(
        link_api2testclient(resp_request_create.json["links"]["self"]),
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {"thesis": record1["id"]}

    resp = creator_client.get(
        link_api2testclient(resp_request_create.json["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    print(json.dumps(resp.json, indent=2))
    assert resp.json["topic"] == {"thesis": record1["id"]}
    assert resp.json["expanded"]["topic"] == {
        "id": record1["id"],
        "metadata": {"title": "Deleted record"},
    }


def test_ui_resolve_topic(
    db,
    vocab_cf,
    logged_client,
    record_factory,
    users,
    urls,
    delete_record_data_function,
    record_service,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=delete_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    assert resp_request_submit.json["status"] == "submitted"

    resp = creator_client.get(
        link_api2testclient(resp_request_create.json["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {
        "reference": {"thesis": record1["id"]},
        "type": "thesis",
        "label": "blabla",
        "links": {
            "self": f"https://127.0.0.1:5000/api/thesis/{record1['id']}",
            "self_html": f"https://127.0.0.1:5000/thesis/{record1['id']}",
        },
    }
    assert resp.json["stateful_name"] == "Record deletion requested"
    assert resp.json["stateful_description"] == (
        "Permission to delete record requested. "
        "You will be notified about the decision by email."
    )

    record_service.delete(system_identity, record1["id"])
    ThesisRecord.index.refresh()

    resp = creator_client.get(
        link_api2testclient(resp_request_create.json["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    print(json.dumps(resp.json, indent=2))
    assert resp.json["topic"] == {
        "reference": {
            "thesis": record1["id"],
        },
        "status": "deleted",
    }
    assert resp.json["stateful_name"] == "Delete record"
    assert resp.json["stateful_description"] == "Request deletion of published record"
