import copy

from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.resolvers.ui import FallbackEntityReferenceUIResolver

from .utils import is_valid_subdict, link_api2testclient


def test_publish(
    users,
    urls,
    publish_request_data_function,
    ui_serialization_result,
    logged_client_request,
    search_clear,
):
    creator = users[0]

    draft1 = logged_client_request(creator, "post", urls["BASE_URL"], json={})
    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = logged_client_request(
        creator, "get", f"{urls['BASE_URL']}{draft_id}/draft"
    ).json
    ui_record = logged_client_request(
        creator,
        "get",
        f"{urls['BASE_URL']}{draft_id}/draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json

    assert is_valid_subdict(
        ui_serialization_result(draft_id, ui_record["requests"][0]["id"]),
        ui_record["requests"][0],
    )


def test_resolver_fallback(
    app,
    users,
    urls,
    publish_request_data_function,
    ui_serialization_result,
    logged_client_request,
    search_clear,
):
    config_restore = copy.deepcopy(app.config["ENTITY_REFERENCE_UI_RESOLVERS"])
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = {
        "fallback": FallbackEntityReferenceUIResolver("fallback"),
    }

    creator = users[0]

    draft1 = logged_client_request(creator, "post", urls["BASE_URL"], json={})
    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = logged_client_request(
        creator,
        "post",
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )

    resp_request_submit = logged_client_request(
        creator,
        "post",
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    ui_record = logged_client_request(
        creator,
        "post",
        f"{urls['BASE_URL']}{draft_id}/draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json
    expected_result = ui_serialization_result(draft_id, ui_record["requests"][0]["id"])
    expected_result["created_by"][
        "label"
    ] = f"id: {creator.id}"  # the user resolver uses name or email as label, the fallback doesn't know what to use
    assert is_valid_subdict(
        expected_result,
        ui_record["requests"][0],
    )
    app.config["ENTITY_REFERENCE_UI_RESOLVERS"] = config_restore
