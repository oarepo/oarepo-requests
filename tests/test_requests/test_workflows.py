#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError

from tests.conftest import TestEventType


def test_publish_with_workflows(
    requests_model,
    logged_client,
    users,
    urls,
    draft_factory,
    create_request_on_draft,
    record_service,
    link2testclient,
    get_action_url,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity, expand=True)
    draft1_id = draft1["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    # test record owner can create publish request
    create_non_owner = receiver_client.post(get_action_url(draft1["expanded"]["request_types"], "publish_draft"))
    resp_request_create = create_request_on_draft(creator.identity, draft1_id, "publish_draft")
    assert create_non_owner.status_code == 403

    resp_request_submit = creator_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
    )
    assert resp_request_submit.status_code == 200

    # test state of the record is changed to published
    draft_with_submitted_request = record_service.read_draft(creator.identity, draft1_id)._record  # noqa SLF001
    assert draft_with_submitted_request["state"] == "publishing"

    record_creator = creator_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true").json
    record_receiver = receiver_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true").json

    assert "accept" not in record_creator["expanded"]["requests"][0]["links"]["actions"]
    assert {"accept", "decline"} == record_receiver["expanded"]["requests"][0]["links"]["actions"].keys()

    accept = receiver_client.post(
        link2testclient(record_receiver["expanded"]["requests"][0]["links"]["actions"]["accept"]),
    )
    assert accept.status_code == 200
    record_cls = requests_model.Record
    published_record = record_cls.pid.resolve(draft1_id)
    assert published_record["state"] == "published"


def test_if_no_new_version_draft(
    logged_client,
    users,
    urls,
    submit_request_on_record,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    record_id = record["id"]
    record2_id = record2["id"]

    record = creator_client.get(
        f"{urls['BASE_URL']}/{record_id}?expand=true",
    ).json
    requests = record["expanded"]["request_types"]
    assert "new_version" in {r["type_id"] for r in requests}

    resp_request_submit = submit_request_on_record(creator.identity, record_id, "new_version")

    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}/{record_id}?expand=true",
    ).json
    requests = record["expanded"]["request_types"]
    assert "new_version" not in {
        r["type_id"] for r in requests
    }  # new version created, requests should not be available again

    resp_request_submit = submit_request_on_record(creator.identity, record2_id, "edit_published_record")
    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"

    # the new version is still not available, as there is an already existing draft

    record = creator_client.get(
        f"{urls['BASE_URL']}/{record2_id}?expand=true",
    ).json
    requests = record["expanded"]["request_types"]
    assert "new_version" not in {r["type_id"] for r in requests}

    # TODO: publish and check?


def test_if_no_edit_draft(
    logged_client,
    users,
    urls,
    record_factory,
    submit_request_on_record,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record = record_factory(creator.identity)
    record2 = record_factory(creator.identity)
    id_ = record["id"]
    id2_ = record2["id"]

    record = creator_client.get(
        f"{urls['BASE_URL']}/{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "edit_published_record" in {r["type_id"] for r in requests}
    resp_request_submit = submit_request_on_record(creator.identity, id_, "edit_published_record")
    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}/{id_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    assert "edit_published_record" not in {
        r["type_id"] for r in requests
    }  # new version created, requests should not be available again

    # try if edit_published_record is still allowed?# ; does it make sense edit request while also creating new version?
    record = creator_client.get(
        f"{urls['BASE_URL']}/{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    resp_request_submit = submit_request_on_record(creator.identity, id2_, "new_version")

    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json  # request is autoaccepted
    assert request["status"] == "accepted"
    record = creator_client.get(
        f"{urls['BASE_URL']}/{id2_}?expand=true",
    )
    requests = record.json["expanded"]["request_types"]
    # edit record is in progress, so edit_published_record is not available
    assert "edit_published_record" not in {r["type_id"] for r in requests}


def test_workflow_events(
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    record_service,
    serialization_result,
    ui_serialization_result,
    events_resource_data,
    draft_factory,
    events_service,
    link2testclient,
    search_clear,
):
    user1 = users[0]
    user2 = users[1]

    user1_client = logged_client(user1)
    user2_client = logged_client(user2)

    draft1 = draft_factory(user1.identity, custom_workflow="with_approve_without_generic")
    record_id = draft1["id"]

    submit_request_on_draft(user1.identity, record_id, "approve_draft")

    read_from_record = user1_client.get(
        f"{urls['BASE_URL']}/{record_id}/draft?expand=true",
    )

    request_id = read_from_record.json["expanded"]["requests"][0]["id"]
    with pytest.raises(PermissionDeniedError):
        events_service.create(
            identity=user1.identity,
            request_id=request_id,
            data=events_resource_data,
            event_type=TestEventType,
        )
    create_event_u2 = events_service.create(
        identity=user2.identity,
        request_id=request_id,
        data=events_resource_data,
        event_type=TestEventType,
    )
    assert create_event_u2

    record_receiver = user2_client.get(f"{urls['BASE_URL']}/{record_id}/draft?expand=true").json
    accept = user2_client.post(
        link2testclient(record_receiver["expanded"]["requests"][0]["links"]["actions"]["accept"]),
    )
    assert accept.status_code == 200

    # TODO: rest depends on autorequest


def test_cancel_transition(
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = draft_factory(creator.identity)
    draft_id = draft1["id"]
    submit_request_on_draft(creator.identity, draft_id, "publish_draft")
    record = creator_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "cancel",
    }
    assert record.json["state"] == "publishing"
    creator_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["cancel"]),
    )

    record = creator_client.get(f"{urls['BASE_URL']}/{draft_id}/draft?expand=true")
    assert record.json["state"] == "draft"
