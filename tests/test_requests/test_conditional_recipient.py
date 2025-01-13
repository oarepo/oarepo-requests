#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
def test_conditional_receiver_creator_matches(
    logged_client,
    users,
    urls,
    create_request_by_link,
    draft_factory,
    search_clear,
):
    # user[0] is creator, user[1] is receiver
    # user[0] is not a creator, user[2] is receiver

    creator = users[0]
    assert creator.id == "1"

    creator_client = logged_client(creator)

    draft1 = draft_factory(creator_client, custom_workflow="with_ct")

    resp_request_create = create_request_by_link(
        creator_client, draft1, "conditional_recipient_rt"
    )

    assert resp_request_create.status_code == 201
    assert resp_request_create.json["receiver"] == {"user": "2"}


def test_conditional_receiver_creator_does_not_match(
    logged_client,
    users,
    urls,
    create_request_by_link,
    draft_factory,
    search_clear,
):
    # user[0] is creator, user[1] is receiver
    # user[0] is not a creator, user[2] is receiver

    creator = users[1]
    assert creator.id != 1

    creator_client = logged_client(creator)

    draft1 = draft_factory(creator_client, custom_workflow="with_ct")

    resp_request_create = create_request_by_link(
        creator_client, draft1, "conditional_recipient_rt"
    )

    assert resp_request_create.status_code == 201
    assert resp_request_create.json["receiver"] == {"user": "3"}
