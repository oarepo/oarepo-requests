#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from thesis.records.api import ThesisDraft, ThesisRecord

from pytest_oarepo.functions import link2testclient


def test_edit_autoaccept(
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
    id_ = record1.json["id"]

    # test direct edit is forbidden
    direct_edit = creator_client.post(
        f"{urls['BASE_URL']}{id_}/draft",
    )
    assert direct_edit.status_code == 403

    resp_request_submit = submit_request_by_link(
        creator_client, record1, "edit_published_record"
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit.json["id"]}',
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    assert "draft_record:links:self" in request["payload"]
    assert "draft_record:links:self_html" in request["payload"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    # edit action worked?
    search = creator_client.get(
        f'user{urls["BASE_URL"]}',
    ).json[
        "hits"
    ]["hits"]
    assert len(search) == 1
    assert search[0]["links"]["self"].endswith("/draft")
    assert search[0]["id"] == id_


def test_redirect_url(
    logged_client,
    users,
    urls,
    submit_request_by_link,
    record_factory,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator_client, custom_workflow="different_recipients")
    record_id = record1.json["id"]

    resp_request_submit = submit_request_by_link(
        creator_client, record1, "edit_published_record"
    )
    edit_request_id = resp_request_submit.json["id"]

    receiver_get = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{edit_request_id}")
    resp_request_accept = receiver_client.post(
        link2testclient(receiver_get.json["links"]["actions"]["accept"])
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{edit_request_id}',
    ).json

    creator_edit_accepted = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{edit_request_id}',
    ).json
    receiver_edit_accepted = receiver_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{edit_request_id}',
    ).json  # receiver should be able to get the request but not to edit the draft - should not receive edit link

    assert (
        link2testclient(creator_edit_accepted["links"]["ui_redirect_url"], ui=True)
        == f"/thesis/{record_id}/edit"
    )
    assert receiver_edit_accepted["links"]["ui_redirect_url"] == None

    draft = creator_client.get(f"{urls['BASE_URL']}{record_id}/draft")
    publish_request = submit_request_by_link(creator_client, draft, "publish_draft")
    receiver_edit_request_after_publish_draft_submitted = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}"
    ).json  # now receiver should have a right to view but not edit the topic
    assert (
        link2testclient(
            receiver_edit_request_after_publish_draft_submitted["links"][
                "ui_redirect_url"
            ],
            ui=True,
        )
        == f"/thesis/{record_id}/preview"
    )

    receiver_publish_request = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request.json['id']}"
    ).json
    receiver_client.post(
        link2testclient(receiver_publish_request["links"]["actions"]["accept"])
    )

    creator_edit_request_after_merge = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{edit_request_id}',
    ).json
    assert (
        creator_edit_request_after_merge["links"]["ui_redirect_url"] == None
    )  # draft now doesn't exist so we can't redirect to it
