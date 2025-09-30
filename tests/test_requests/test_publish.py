#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

import copy


def test_publish_service(
    requests_model,
    users,
    record_service,
    default_record_with_workflow_json,
    search_clear,
):
    from invenio_requests.proxies import current_requests_service

    creator = users[0]
    receiver = users[1]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    request = current_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,  # noqa SLF001
        expand=True,
    )
    requests_model.Draft.index.refresh()
    submit_result = current_requests_service.execute_action(creator.identity, request.id, "submit", expand=True)
    # the entity links taken from expanded won't show in RequestItem.links if something's dependent on that
    assert "self" in request.data["expanded"]["created_by"]["links"]
    assert "self" in request.data["expanded"]["receiver"]["links"]
    assert "self" in request.data["expanded"]["topic"]["links"]
    assert "self_html" in request.data["expanded"]["topic"]["links"]
    assert "payload" not in request.data["expanded"]

    assert "self" in submit_result.data["expanded"]["created_by"]["links"]
    assert "self" in submit_result.data["expanded"]["receiver"]["links"]
    assert "self" in submit_result.data["expanded"]["topic"]["links"]
    assert "self_html" in submit_result.data["expanded"]["topic"]["links"]
    assert "payload" not in submit_result.data["expanded"]

    accept = current_requests_service.execute_action(receiver.identity, request.id, "accept", expand=True)

    assert "self" in accept.data["expanded"]["created_by"]["links"]
    assert "self" in accept.data["expanded"]["receiver"]["links"]
    assert accept.data["expanded"]["topic"]["links"] == {}
    assert accept.data["expanded"]["topic"]["metadata"] == {
        "title": "Deleted record"
    }  # TODO: created topic is not indexed at the init of publish result
    assert "self" in accept.data["expanded"]["payload"]["created_topic"]["links"]
    assert "self_html" in accept.data["expanded"]["payload"]["created_topic"]["links"]

    record_service.read(creator.identity, draft["id"])  # will throw exception if record isn't published


def test_publish(
    requests_model,
    logged_client,
    users,
    urls,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft2 = draft_factory(creator.identity)
    draft3 = draft_factory(creator.identity)
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]
    draft3_id = draft3["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls["BASE_URL"], query_string={"record_status": "published"})
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 0

    resp_request_submit = submit_request_on_draft(creator.identity, draft1_id, "publish_draft")
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    record = receiver_client.get(f"{urls['BASE_URL']}/{draft1_id}/draft?expand=true")
    creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}?expand=true",
    )
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    receiver_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]),
    )

    receiver_client.get(f"{urls['BASE_URL']}/{draft1_id}?expand=true")

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls["BASE_URL"], query_string={"record_status": "published"})
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 1

    resp_request_submit = submit_request_on_draft(creator.identity, draft2_id, "publish_draft")
    record = receiver_client.get(f"{urls['BASE_URL']}/{draft2_id}/draft?expand=true")
    receiver_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]),
    )
    declined_request = creator_client.get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    assert declined_request.json["status"] == "declined"

    resp_request_submit = submit_request_on_draft(creator.identity, draft3_id, "publish_draft")
    record = creator_client.get(f"{urls['BASE_URL']}/{draft3_id}/draft?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {"cancel"}
    creator_client.post(
        link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["cancel"]),
    )
    canceled_request = logged_client(creator).get(f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}")
    assert canceled_request.json["status"] == "cancelled"


def test_create_fails_if_draft_not_validated(
    logged_client,
    users,
    urls,
    draft_factory,
    default_record_with_workflow_json,
    link2testclient,
    find_request_type,
    search_clear,
):
    creator = users[0]

    creator_client = logged_client(creator)

    json = copy.deepcopy(default_record_with_workflow_json)
    del json["metadata"]["title"]

    draft = creator_client.post(f"{urls['BASE_URL']}?expand=true", json=json)

    assert "publish_draft" not in draft.json["expanded"]["request_types"]
    resp_request_create = creator_client.post(
        link2testclient(
            find_request_type(draft.json["expanded"]["request_types"], "publish_draft")["links"]["actions"]["create"]
        )
    )
    assert resp_request_create.status_code == 400
    assert resp_request_create.json["message"] == "A validation error occurred."
    assert resp_request_create.json["errors"] == [
        {"field": "metadata.title", "messages": ["Missing data for required field."]}
    ]
