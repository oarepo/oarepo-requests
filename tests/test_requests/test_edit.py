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

    resp_request_submit = submit_request_on_record(
        creator.identity, id_, "edit_published_record"
    )
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


def test_publish(
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_record,
    submit_request_on_draft,
    link2testclient,
    record_with_files_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    receiver_client = logged_client(users[1])

    record1 = record_with_files_factory(creator.identity)
    id_ = record1["id"]

    submit_request_on_record(creator.identity, id_, "edit_published_record")

    creator_client.put(
        f"{urls['BASE_URL']}/{id_}/draft", json={"metadata": {"title": "edited"}}
    )
    publish_request = submit_request_on_draft(
        creator.identity, id_, "publish_changed_metadata"
    )
    receiver_request = receiver_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request['id']}"
    )
    receiver_client.post(
        link2testclient(receiver_request.json["links"]["actions"]["accept"])
    )

    # check it's published
    new_record = creator_client.get(f"{urls['BASE_URL']}/{id_}")
    assert new_record.status_code == 200
    assert new_record.json["metadata"]["title"] == "edited"
