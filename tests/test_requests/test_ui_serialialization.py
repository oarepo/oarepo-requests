
from thesis.records.api import ThesisDraft, ThesisRecord

from .utils import link_api2testclient, is_valid_subdict


def test_publish(
    client_logged_as,
    users,
    urls,
    publish_request_data_function,
    ui_serialization_result,
):
    creator_client = client_logged_as(users[0].email)

    receiver = users[1]

    draft1 = creator_client.post(urls["BASE_URL"], json={})
    draft_id = draft1.json["id"]
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"], json=publish_request_data_function(receiver.id, draft1.json["id"])
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    receiver_client = client_logged_as(users[1].email)
    record = receiver_client.get(f"{urls['BASE_URL']}{draft_id}/draft").json
    ui_record = receiver_client.get(
        f"{urls['BASE_URL']}{draft_id}/draft",
        headers={"Accept": "application/vnd.inveniordm.v1+json"},
    ).json

    assert is_valid_subdict(
        ui_serialization_result(draft_id, ui_record["requests"][0]['id']), ui_record["requests"][0]
    )
