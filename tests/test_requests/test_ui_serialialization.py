import copy
from pprint import pprint

from deepdiff import DeepDiff
from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.resolvers.ui import FallbackEntityReferenceUIResolver

from .utils import is_valid_subdict, link_api2testclient


def test_publish(
    users,
    urls,
    publish_request_data_function,
    ui_serialization_result,
    create_draft_via_resource,
    logged_client,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)
    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    pprint(resp_request_create.json)
    assert resp_request_create.json["stateful_name"] == "Submit for review"
    assert resp_request_create.json["stateful_description"] == (
        "Submit for review. After submitting the draft for review, "
        "it will be locked and no further modifications will be possible."
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    pprint(resp_request_submit.json)
    assert resp_request_submit.json["stateful_name"] == "Submitted for review"
    assert (
        resp_request_submit.json["stateful_description"]
        == "The draft has been submitted for review. It is now locked and no further changes are possible. You will be notified about the decision by email."
    )

    record = creator_client.get(f"{urls['BASE_URL']}{draft_id}/draft").json
    ui_record = creator_client.get(
        f"{urls['BASE_URL']}{draft_id}/draft?expand=true",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    diff = DeepDiff(
        ui_serialization_result(draft_id, ui_record["expanded"]["requests"][0]["id"]),
        ui_record["expanded"]["requests"][0],
    )
    assert "dictionary_item_removed" not in diff
    assert "dictionary_item_changed" not in diff


def test_resolver_fallback(
    app,
    users,
    urls,
    publish_request_data_function,
    ui_serialization_result,
    create_draft_via_resource,
    logged_client,
    search_clear,
):
    config_restore = copy.deepcopy(app.config["ENTITY_REFERENCE_UI_RESOLVERS"])
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = {
        "fallback": FallbackEntityReferenceUIResolver("fallback"),
    }

    creator = users[0]
    creator_client = logged_client(creator)

    draft1 = create_draft_via_resource(creator_client)
    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    )
    assert resp_request_create.json["stateful_name"] == "Submit for review"
    assert (
        resp_request_create.json["stateful_description"]
        == "Submit for review. After submitting the draft for review, it will be locked and no further modifications will be possible."
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
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
    assert is_valid_subdict(
        expected_result,
        ui_record["expanded"]["requests"][0],
    )
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = config_restore


def test_role(
    app,
    users,
    role,
    urls,
    publish_request_data_function,
    logged_client,
    role_ui_serialization,
    create_draft_via_resource,
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

        draft1 = create_draft_via_resource(creator_client)
        draft_id = draft1.json["id"]
        ThesisRecord.index.refresh()
        ThesisDraft.index.refresh()

        resp_request_create = creator_client.post(
            urls["BASE_URL_REQUESTS"],
            json=publish_request_data_function(draft1.json["id"]),
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
