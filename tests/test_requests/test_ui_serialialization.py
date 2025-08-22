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


from oarepo_requests.resolvers.ui import FallbackEntityReferenceUIResolver
from pytest_oarepo.functions import clear_babel_context

def test_user_serialization(
    requests_model,
    users,
    urls,
    ui_serialization_result,
    draft_factory,
    logged_client,
    user_links,
    create_request_on_draft,
    link2testclient,
    search_clear,
):
    clear_babel_context()
    fallback_label = users[0]
    username_label = users[1]
    fullname_label = users[2]

    fallback_label_client = logged_client(users[0])
    username_label_client = logged_client(users[1])
    fullname_label_client = logged_client(users[2])

    draft1 = draft_factory(fallback_label.identity)
    draft2 = draft_factory(username_label.identity)
    draft3 = draft_factory(fullname_label.identity)
    draft1_id = draft1["id"]
    draft2_id = draft2["id"]
    draft3_id = draft3["id"]

    draft_id = draft1_id
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    resp_request_create = create_request_on_draft(
        fallback_label.identity, draft1_id, "publish_draft"
    )
    resp_request_create = fallback_label_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_create['id']}",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    resp_request_create_username = create_request_on_draft(
        username_label.identity,
        draft2_id,
        "publish_draft",
    )
    resp_request_create_fullname = create_request_on_draft(
        fullname_label.identity,
        draft3_id,
        "publish_draft",
    )

    pprint(resp_request_create)
    assert resp_request_create["stateful_name"] == "Submit for review"
    assert resp_request_create["stateful_description"] == (
        "Submit for review. After submitting the draft for review, "
        "it will be locked and no further modifications will be possible."
    )

    resp_request_submit = fallback_label_client.post(
        link2testclient(resp_request_create["links"]["actions"]["submit"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    pprint(resp_request_submit.json)
    assert resp_request_submit.json["stateful_name"] == "Draft submitted for review"
    assert (
        resp_request_submit.json["stateful_description"]
        == "The draft has been submitted for review. It is now locked and no further changes are possible. You will be notified about the decision by email."
    )

    record = fallback_label_client.get(f"{urls['BASE_URL']}{draft_id}/draft").json
    ui_record = fallback_label_client.get(
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

    ui_record_username = username_label_client.get(
        f"{urls['BASE_URL']}{draft2_id}/draft?expand=true",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    ui_record_fullname = fullname_label_client.get(
        f"{urls['BASE_URL']}{draft3_id}/draft?expand=true",
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
    requests_model,
    users,
    urls,
    ui_serialization_result,
    draft_factory,
    create_request_on_draft,
    logged_client,
    link2testclient,
    search_clear,
):
    clear_babel_context()
    config_restore = copy.deepcopy(app.config["ENTITY_REFERENCE_UI_RESOLVERS"])
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = {
        "fallback": FallbackEntityReferenceUIResolver("fallback"),
    }
    try:
        creator = users[0]
        creator_client = logged_client(creator)

        draft1 = draft_factory(creator.identity)
        draft_id = draft1["id"]
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        resp_request_create = create_request_on_draft(
            creator.identity, draft_id, "publish_draft"
        )
        request_id = resp_request_create["id"]
        ui_serialization_read = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{request_id}",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ).json
        assert ui_serialization_read["stateful_name"] == "Submit for review"
        assert (
            ui_serialization_read["stateful_description"]
            == "Submit for review. After submitting the draft for review, it will be locked and no further modifications will be possible."
        )

        resp_request_submit = creator_client.post(
            link2testclient(resp_request_create["links"]["actions"]["submit"])
        )
        ui_serialization_read_submitted = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{request_id}",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ).json
        assert (
            ui_serialization_read_submitted["stateful_name"]
            == "Draft submitted for review"
        )
        assert (
            ui_serialization_read_submitted["stateful_description"]
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
    requests_model,
    users,
    role,
    urls,
    create_request_on_draft,
    logged_client,
    role_ui_serialization,
    draft_factory,
    search_clear,
):
    clear_babel_context()
    config_restore = app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]

    def current_receiver(record=None, request_type=None, **kwargs):
        if request_type.type_id == "publish_draft":
            return role
        return config_restore(record, request_type, **kwargs)

    try:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = current_receiver

        creator = users[0]
        creator_client = logged_client(creator)

        draft1 = draft_factory(creator.identity)
        draft_id = draft1["id"]
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        resp_request_create = create_request_on_draft(
            creator.identity,
            draft_id,
            "publish_draft",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        )
        ui_serialization_read = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{resp_request_create['id']}",
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
        ).json
        assert ui_serialization_read["stateful_name"] == "Submit for review"
        assert (
            ui_serialization_read["stateful_description"]
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
    submit_request_on_record,
    record_factory,
    search_clear,
):
    clear_babel_context()
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)

    resp_request_submit = submit_request_on_record(
        creator.identity, record1["id"], "new_version"
    )
    # is request accepted and closed?
    request_json = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json

    assert request_json["receiver"]["label"] == "Auto approve"
