#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations


def test_edit_autoaccept(
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_record,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    id_ = record1["id"]

    # test direct edit is forbidden
    direct_edit = creator_client.post(
        f"{urls['BASE_URL']}/{id_}/draft",
    )
    assert direct_edit.status_code == 403

    resp_request_submit = submit_request_on_record(creator.identity, id_, "edit_published_record")
    # is request accepted and closed?
    request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{resp_request_submit['id']}",
    ).json

    assert request["status"] == "accepted"
    assert not request["is_open"]
    assert request["is_closed"]

    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    # edit action worked?
    search = creator_client.get(
        f"user{urls['BASE_URL']}",
    ).json["hits"]["hits"]
    assert len(search) == 1
    # mypy assert search[0]["links"]["self"].endswith( # TODO: should self after edit point to published or draft?
    #    "/draft"
    # mypy )
    assert search[0]["id"] == id_


def test_redirect_url(
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_record,
    submit_request_on_draft,
    record_factory,
    link2testclient,
    search_clear,
):
    # whether the created topic is accessible now depends on permissions to see
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    record1 = record_factory(creator.identity, custom_workflow="different_recipients")
    record_id = record1["id"]

    resp_request_submit = submit_request_on_record(creator.identity, record_id, "edit_published_record")
    edit_request_id = resp_request_submit["id"]

    receiver_get = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{edit_request_id}")
    receiver_client.post(link2testclient(receiver_get.json["links"]["actions"]["accept"]))
    # is request accepted and closed?
    creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}",
    )
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    creator_edit_accepted = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}?expand=true",
    ).json
    receiver_edit_accepted = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}?expand=true",
    ).json  # receiver should be able to get the request but not to edit the draft - should not receive edit link

    # also why it shows receiver links?
    # TODO: test links now give 404/ wait for ui implementation?
    creator_client.get(
        link2testclient(
            creator_edit_accepted["expanded"]["payload"]["created_topic"]["links"]["self_html"],
            ui=True,
        )
    )
    # TODO: i assume using will be a tweak on ui side
    # the problem here is that link to draft_html isn't in search_links?
    assert (
        link2testclient(
            creator_edit_accepted["expanded"]["payload"]["created_topic"]["links"]["self_html"],
            ui=True,
        )
        == f"/api/test-ui-links/uploads/{record_id}"  # draft self_html now goes to deposit_upload
    )

    assert receiver_edit_accepted["expanded"]["payload"]["created_topic"]["links"] == {}

    draft = creator_client.get(f"{urls['BASE_URL']}/{record_id}/draft").json
    publish_request = submit_request_on_draft(creator.identity, draft["id"], "publish_draft")
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    receiver_edit_request_after_publish_draft_submitted = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}?expand=true"
    ).json  # now receiver should have a right to view but not edit the topic
    assert (
        receiver_edit_request_after_publish_draft_submitted["expanded"]["payload"]["created_topic"]["links"] == {}
    )  # receiver doesn't have permission to topic

    receiver_publish_request = receiver_client.get(f"{urls['BASE_URL_REQUESTS']}{publish_request['id']}").json
    receiver_client.post(link2testclient(receiver_publish_request["links"]["actions"]["accept"]))
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()
    creator_edit_request_after_merge = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{edit_request_id}?expand=true",
    ).json

    assert creator_edit_request_after_merge["expanded"]["payload"]["created_topic"]["links"] == {}
