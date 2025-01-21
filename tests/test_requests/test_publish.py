#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import copy

from thesis.records.api import ThesisDraft, ThesisRecord


def test_publish_service(
    users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    creator = users[0]
    receiver = users[1]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    request = current_oarepo_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,
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

    accept_result = current_invenio_requests_service.execute_action(
        receiver.identity, request.id, "accept"
    )

    record_service.read(
        creator.identity, draft["id"]
    )  # will throw exception if record isn't published


def test_publish(
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
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls["BASE_URL"])
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 0

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = receiver_client.get(f"{urls['BASE_URL']}{draft1_id}/draft?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )

    assert "published_record:links:self" in publish.json["payload"]
    assert "published_record:links:self_html" in publish.json["payload"]

    published_record = receiver_client.get(f"{urls['BASE_URL']}{draft1_id}?expand=true")

    assert "version" in published_record.json["metadata"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{urls['BASE_URL']}")
    lst = creator_client.get(urls["BASE_URL"])
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 1

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft2_id, "publish_draft"
    )
    record = receiver_client.get(f"{urls['BASE_URL']}{draft2_id}/draft?expand=true")
    decline = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )
    declined_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}"
    )
    assert declined_request.json["status"] == "declined"

    resp_request_submit = submit_request_on_draft(
        creator.identity, draft3_id, "publish_draft"
    )
    record = creator_client.get(f"{urls['BASE_URL']}{draft3_id}/draft?expand=true")
    assert record.json["expanded"]["requests"][0]["links"]["actions"].keys() == {
        "cancel"
    }
    cancel = creator_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["cancel"]
        ),
    )
    canceled_request = logged_client(creator).get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"


def test_create_fails_if_draft_not_validated(
    logged_client,
    users,
    urls,
    draft_factory,
    default_record_with_workflow_json,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)

    json = copy.deepcopy(default_record_with_workflow_json)
    del json["metadata"]["title"]

    draft = creator_client.post(f"{urls['BASE_URL']}?expand=true", json=json)

    assert "publish_draft" not in draft.json["expanded"]["request_types"]
    resp_request_create = creator_client.post(
        f"{urls["BASE_URL"]}{draft.json['id']}/draft/requests/publish_draft",
    )
    assert resp_request_create.status_code == 400
    assert resp_request_create.json["message"] == "A validation error occurred."
    assert resp_request_create.json["errors"] == [
        {"field": "metadata.title", "messages": ["Missing data for required field."]}
    ]
