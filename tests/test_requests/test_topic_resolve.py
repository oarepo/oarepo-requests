#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import json

from invenio_access.permissions import system_identity
from pytest_oarepo.functions import link2testclient
from thesis.records.api import ThesisDraft, ThesisRecord


def test_resolve_topic(
    db,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_by_link,
    record_service,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator_client)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_submit = submit_request_by_link(
        creator_client, record1, "delete_published_record"
    )
    assert resp_request_submit.json["status"] == "submitted"

    resp = creator_client.get(
        link2testclient(resp_request_submit.json["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    assert resp.json["expanded"]["topic"] == {
        "id": record1.json["id"],
        "metadata": {
            "contributors": ["Contributor 1"],
            "creators": ["Creator 1", "Creator 2"],
            "title": "blabla",
        },
    }

    record_service.delete(system_identity, record1.json["id"])
    ThesisRecord.index.refresh()

    resp = creator_client.get(
        link2testclient(resp_request_submit.json["links"]["self"]),
    )
    assert resp.status_code == 200
    assert resp.json["topic"] == {"thesis": record1.json["id"]}

    resp = creator_client.get(
        link2testclient(resp_request_submit.json["links"]["self"]),
        query_string={"expand": "true"},
    )
    assert resp.status_code == 200
    print(json.dumps(resp.json, indent=2))
    assert resp.json["topic"] == {"thesis": record1.json["id"]}
    assert resp.json["expanded"]["topic"] == {
        "id": record1.json["id"],
        "metadata": {"title": "Deleted record"},
    }


def test_ui_resolve_topic(
    db,
    logged_client,
    record_factory,
    users,
    urls,
    submit_request_by_link,
    record_service,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator_client)
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_submit = submit_request_by_link(
        creator_client, record1, "delete_published_record"
    )
    assert resp_request_submit.json["status"] == "submitted"

    resp = creator_client.get(
        link2testclient(resp_request_submit.json["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    assert (
        resp.json["topic"].items()
        >= {
            "reference": {"thesis": record1.json["id"]},
            "type": "thesis",
            "label": "blabla",
        }.items()
    )
    assert (
        resp.json["topic"]["links"].items()
        >= {
            "self": f"https://127.0.0.1:5000/api/thesis/{record1.json["id"]}",
            "self_html": f"https://127.0.0.1:5000/thesis/{record1.json["id"]}",
        }.items()
    )
    assert resp.json["stateful_name"] == "Record deletion requested"
    assert resp.json["stateful_description"] == (
        "Permission to delete record requested. "
        "You will be notified about the decision by email."
    )

    record_service.delete(system_identity, record1.json["id"])
    ThesisRecord.index.refresh()

    resp = creator_client.get(
        link2testclient(resp_request_submit.json["links"]["self"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp.status_code == 200
    print(json.dumps(resp.json, indent=2))
    assert resp.json["topic"] == {
        "reference": {
            "thesis": record1.json["id"],
        },
        "status": "deleted",
    }
    assert resp.json["stateful_name"] == "Delete record"
    assert resp.json["stateful_description"] == "Request deletion of published record"
