#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import copy
from pprint import pprint

from deepdiff import DeepDiff
from pytest_oarepo.functions import link2testclient
from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.resolvers.ui import FallbackEntityReferenceUIResolver


def test_user_serialization(
    users,
    urls,
    ui_serialization_result,
    draft_factory,
    logged_client,
    user_links,
    create_request_by_link,
    search_clear,
):
    client_fallback_label = logged_client(users[0])
    client_username_label = logged_client(users[1])
    client_fullname_label = logged_client(users[2])

    draft1 = draft_factory(client_fallback_label)
    draft2 = draft_factory(client_username_label)
    draft3 = draft_factory(client_fullname_label)

    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = create_request_by_link(
        client_fallback_label,
        draft1,
        "publish_draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    resp_request_create_username = create_request_by_link(
        client_username_label,
        draft2,
        "publish_draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    resp_request_create_fullname = create_request_by_link(
        client_fullname_label,
        draft3,
        "publish_draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )

    pprint(resp_request_create.json)
    assert resp_request_create.json["stateful_name"] == "Submit for review"
    assert resp_request_create.json["stateful_description"] == (
        "Submit for review. After submitting the draft for review, "
        "it will be locked and no further modifications will be possible."
    )

    resp_request_submit = client_fallback_label.post(
        link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    pprint(resp_request_submit.json)
    assert resp_request_submit.json["stateful_name"] == "Submitted for review"
    assert (
        resp_request_submit.json["stateful_description"]
        == "The draft has been submitted for review. It is now locked and no further changes are possible. You will be notified about the decision by email."
    )

    record = client_fallback_label.get(f"{urls['BASE_URL']}{draft_id}/draft").json
    ui_record = client_fallback_label.get(
        f"{urls['BASE_URL']}{draft_id}/draft?expand=true",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    diff = DeepDiff(
        ui_serialization_result(draft_id, ui_record["expanded"]["requests"][0]["id"]),
        ui_record["expanded"]["requests"][0],
    )
    assert "dictionary_item_removed" not in diff
    assert "dictionary_item_changed" not in diff

    creator_serialization = {
        "label": "id: 1",
        "links": user_links(1),
        "reference": {"user": "1"},
        "type": "user",
    }

    creator_serialization_username = {
        "label": "beetlesmasher",
        "links": user_links(2),
        "reference": {"user": "2"},
        "type": "user",
    }

    creator_serialization_fullname = {
        "label": "Maxipes Fik",
        "links": user_links(3),
        "reference": {"user": "3"},
        "type": "user",
    }

    ui_record_username = client_username_label.get(
        f"{urls['BASE_URL']}{draft2.json['id']}/draft?expand=true",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    ui_record_fullname = client_fullname_label.get(
        f"{urls['BASE_URL']}{draft3.json['id']}/draft?expand=true",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json

    assert ui_record["expanded"]["requests"][0]["created_by"] == creator_serialization
    assert (
        ui_record_username["expanded"]["requests"][0]["created_by"]
        == creator_serialization_username
    )
    assert (
        ui_record_fullname["expanded"]["requests"][0]["created_by"]
        == creator_serialization_fullname
    )


def test_resolver_fallback(
    app,
    users,
    urls,
    ui_serialization_result,
    draft_factory,
    create_request_by_link,
    logged_client,
    search_clear,
):
    config_restore = copy.deepcopy(app.config["ENTITY_REFERENCE_UI_RESOLVERS"])
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = {
        "fallback": FallbackEntityReferenceUIResolver("fallback"),
    }
    try:
        creator = users[0]
        creator_client = logged_client(creator)

        draft1 = draft_factory(creator_client)
        draft_id = draft1.json["id"]
        ThesisRecord.index.refresh()
        ThesisDraft.index.refresh()

        resp_request_create = create_request_by_link(
            creator_client,
            draft1,
            "publish_draft",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        )
        assert resp_request_create.json["stateful_name"] == "Submit for review"
        assert (
            resp_request_create.json["stateful_description"]
            == "Submit for review. After submitting the draft for review, it will be locked and no further modifications will be possible."
        )

        resp_request_submit = creator_client.post(
            link2testclient(resp_request_create.json["links"]["actions"]["submit"]),
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        )
        assert resp_request_submit.json["stateful_name"] == "Submitted for review"
        assert (
            resp_request_submit.json["stateful_description"]
            == "The draft has been submitted for review. It is now locked and no further changes are possible. You will be notified about the decision by email."
        )

        ui_record = creator_client.get(
            f"{urls['BASE_URL']}{draft_id}/draft?expand=true",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ).json
        expected_result = ui_serialization_result(
            draft_id, ui_record["expanded"]["requests"][0]["id"]
        )
        expected_result["created_by"][
            "label"
        ] = f"id: {creator.id}"  # the user resolver uses name or email as label, the fallback doesn't know what to use
        expected_created_by = {**expected_result["created_by"]}
        actual_created_by = {**ui_record["expanded"]["requests"][0]["created_by"]}

        expected_topic = {**expected_result["topic"]}
        actual_topic = {**ui_record["expanded"]["requests"][0]["topic"]}

        expected_receiver = {**expected_result["receiver"]}
        actual_receiver = {**ui_record["expanded"]["requests"][0]["receiver"]}

        expected_created_by.pop("links", None)
        actual_created_by.pop("links", None)

        expected_topic.pop("links", None)
        actual_topic.pop("links", None)

        assert expected_topic.pop("label") == actual_topic.pop("label")

        expected_receiver.pop("links", None)
        actual_receiver.pop("links", None)

        assert expected_created_by == actual_created_by
        assert expected_topic == actual_topic
        assert expected_receiver == actual_receiver
    finally:
        app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = config_restore


def test_role(
    app,
    users,
    role,
    urls,
    create_request_by_link,
    logged_client,
    role_ui_serialization,
    draft_factory,
    search_clear,
):
    config_restore = app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]

    def current_receiver(record=None, request_type=None, **kwargs):
        if request_type.type_id == "publish_draft":
            return role
        return config_restore(record, request_type, **kwargs)

    try:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = current_receiver

        creator = users[0]
        creator_client = logged_client(creator)

        draft1 = draft_factory(creator_client)
        draft_id = draft1.json["id"]
        ThesisRecord.index.refresh()
        ThesisDraft.index.refresh()

        resp_request_create = create_request_by_link(
            creator_client,
            draft1,
            "publish_draft",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        )
        assert resp_request_create.json["stateful_name"] == "Submit for review"
        assert (
            resp_request_create.json["stateful_description"]
            == "Submit for review. After submitting the draft for review, it will be locked and no further modifications will be possible."
        )

        ui_record = creator_client.get(
            f"{urls['BASE_URL']}{draft_id}/draft?expand=true",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ).json

        assert ui_record["expanded"]["requests"][0]["receiver"] == role_ui_serialization
    finally:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = config_restore


def test_auto_approve(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator_client)

    resp_request_submit = submit_request_by_link(creator_client, record1, "new_version")
    # is request accepted and closed?
    request_json = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit.json["id"]}',
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json

    assert request_json["receiver"]["label"] == "Auto approve"
