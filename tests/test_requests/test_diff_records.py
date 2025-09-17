#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_requests.records.models import RequestEventModel

from oarepo_requests.models import RecordSnapshot


def test_new_record(
    db, users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    creator = users[0]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    request = current_oarepo_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,  # noqa SLF001
    )
    submit_result = current_invenio_requests_service.execute_action(
        creator.identity, request.id, "submit"
    )
    assert "created_by" in request.links
    assert "topic" in request.links
    assert "self" in request.links["topic"]
    # assert "self_html" in request.links["topic"] TODO: temp

    assert "created_by" in submit_result.links
    assert "topic" in submit_result.links
    assert "self" in submit_result.links["topic"]
    # assert "self_html" in submit_result.links["topic"] TODO: temp

    # only 1 snapshot because of new record
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    # no events happened
    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 0


def test_diff_after_publish_is_denied(
    db,
    requests_model,
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    search_clear,
    record_service,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft2 = draft_factory(creator.identity)
    draft2_id = draft2["id"]

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft2_id, "publish_draft"
    )

    # only 1 snapshot because of new record
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    # no events happened
    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 0

    record = receiver_client.get(f"{urls['BASE_URL']}/{draft2_id}/draft?expand=true")
    receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )
    declined_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}"
    )
    assert declined_request.json["status"] == "declined"

    draft2["metadata"]["title"] = "new blahbla title"
    record_service.update_draft(system_identity, draft2["id"], draft2)

    # 2 snapshots now
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 2

    # event with diff should happen
    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 1

    # resubmit draft
    resp_request_submit = submit_request_on_draft(
        creator.identity, draft2_id, "publish_draft"
    )

    # 3 snapshots now
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 3

    # event with diff should happen
    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 2

    assert results[0].json != "[]"


def test_new_version_diff(
    db,
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_record,
    submit_request_on_draft,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]

    new_version_direct = creator_client.post(
        f"{urls['BASE_URL']}/{record1_id}/versions",
    )
    assert new_version_direct.status_code == 403

    resp_request_submit = submit_request_on_record(
        creator.identity, record1_id, "new_version"
    )
    # is request accepted and closed?
    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    assert "draft_record:links:self" in request["payload"]
    assert "draft_record:links:self_html" in request["payload"]

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    # new_version action worked?
    search = creator_client.get(
        f"user{urls['BASE_URL']}?allversions=true",
    ).json["hits"]["hits"]
    assert len(search) == 2
    assert search[0]["id"] != search[1]["id"]
    assert search[0]["parent"]["id"] == search[1]["parent"]["id"]

    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    draft_search = creator_client.get(f"/user{urls['BASE_URL']}").json["hits"]["hits"]
    new_draft = next(
        x
        for x in draft_search
        if x["parent"]["id"] == record1["parent"]["id"] and x["state"] == "draft"
    )

    new_draft = creator_client.get(f"{urls['BASE_URL']}/{new_draft['id']}/draft").json
    new_draft["metadata"]["title"] = "new title"

    assert (
        creator_client.put(
            f"{urls['BASE_URL']}/{new_draft['id']}/draft", json=new_draft
        ).status_code
        == 200
    )

    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 0

    submit_request_on_draft(creator.identity, new_draft["id"], "publish_draft")

    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 2

    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 1

    event = results[0].json
    assert event["payload"]["diff"] != "[]"


def test_edited_metadata_diff(
    db,
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_record,
    submit_request_on_draft,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    record1_id = record1["id"]

    new_version_direct = creator_client.post(
        f"{urls['BASE_URL']}/{record1_id}/versions",
    )
    assert new_version_direct.status_code == 403

    resp_request_submit = submit_request_on_record(
        creator.identity, record1_id, "edit_published_record"
    )
    # is request accepted and closed?
    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    assert "draft_record:links:self" in request["payload"]
    assert "draft_record:links:self_html" in request["payload"]

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    # edit metadata action worked?
    search = creator_client.get(
        f"user{urls['BASE_URL']}?allversions=true",
    ).json["hits"]["hits"]
    assert len(search) == 1

    # should be 1 snapshot with "edited" metadata
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    # no event happened
    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 0

    draft_search = creator_client.get(f"/user{urls['BASE_URL']}").json["hits"]["hits"]
    new_draft = next(
        x
        for x in draft_search
        if x["parent"]["id"] == record1["parent"]["id"] and x["state"] == "draft"
    )

    new_draft = creator_client.get(f"{urls['BASE_URL']}/{new_draft['id']}/draft").json
    new_draft["metadata"]["title"] = "new title"

    assert (
        creator_client.put(
            f"{urls['BASE_URL']}/{new_draft['id']}/draft", json=new_draft
        ).status_code
        == 200
    )

    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 0

    submit_request_on_draft(creator.identity, new_draft["id"], "publish_draft")

    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 2

    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 1


def test_request_active_diff(
    db,
    users,
    default_record_with_workflow_json,
    submit_request_on_draft,
    record_service,
    logged_client,
    urls,
    search_clear,
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    creator = users[0]
    logged_client(creator)

    receiver = users[1]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    request = current_oarepo_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,  # noqa SLF001
    )
    submit_result = current_invenio_requests_service.execute_action(
        creator.identity, request.id, "submit"
    )
    assert "created_by" in request.links
    assert "topic" in request.links
    assert "self" in request.links["topic"]
    assert "self_html" in request.links["topic"]

    assert "created_by" in submit_result.links
    assert "topic" in submit_result.links
    assert "self" in submit_result.links["topic"]
    assert "self_html" in submit_result.links["topic"]

    # should be 1 snapshot after we submitted
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 1

    # request is in submitted state and is active
    # change some metadata
    draft_dict = draft.to_dict()
    draft_dict["metadata"]["title"] = "new blahbla title"
    record_service.update_draft(system_identity, draft_dict["id"], draft_dict)

    # should be 2 snapshots after we changed the record
    results = db.session.query(RecordSnapshot).all()
    assert len(results) == 2

    results = db.session.query(RequestEventModel).filter_by(type="S").all()
    assert len(results) == 1

    current_invenio_requests_service.execute_action(
        receiver.identity, request.id, "accept"
    )

    record_service.read(
        creator.identity, draft["id"]
    )  # will throw exception if record isn't published
