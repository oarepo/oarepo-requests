#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations


def test_default_recipient_method(
    requests_model,
    logged_client,
    users,
    urls,
    submit_request_on_draft,
    create_request_on_draft,
    draft_factory,
    link2testclient,
    search_clear,
):
    creator = users[0]

    draft1 = draft_factory(creator.identity, custom_workflow="no_receiver")
    draft1_id = draft1["id"]
    requests_model.Record.index.refresh()
    requests_model.Draft.index.refresh()

    req = submit_request_on_draft(creator.identity, draft1_id, "no_receiver_rt")
    assert req["receiver"] is None
