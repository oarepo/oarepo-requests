#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations


def test_conditional_receiver_creator_matches(
    requests_model,
    logged_client,
    users,
    urls,
    create_request_on_draft,
    draft_factory,
    search_clear,
):
    # /for mypy - this is not code/ user[0] is creator, user[1] is receiver
    # /for mypy - this is not code/ user[0] is not a creator, user[2] is receiver

    creator = users[0]
    assert creator.id == "1"

    draft1 = draft_factory(creator.identity, custom_workflow="with_ct")

    resp_request_create = create_request_on_draft(creator.identity, draft1["id"], "conditional_recipient_rt")

    assert resp_request_create["receiver"] == {"user": "2"}


def test_conditional_receiver_creator_does_not_match(
    requests_model,
    logged_client,
    users,
    urls,
    create_request_on_draft,
    draft_factory,
    search_clear,
):
    # /for mypy - this is not code/ user[0] is creator, user[1] is receiver
    # /for mypy - this is not code/ user[0] is not a creator, user[2] is receiver

    creator = users[1]
    assert creator.id != 1

    draft1 = draft_factory(creator.identity, custom_workflow="with_ct")

    resp_request_create = create_request_on_draft(creator.identity, draft1["id"], "conditional_recipient_rt")

    assert resp_request_create["receiver"] == {"user": "3"}
