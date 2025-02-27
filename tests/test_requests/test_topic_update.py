#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


def test_publish(
    logged_client,
    users,
    urls,
    draft_factory,
    check_publish_topic_update,
    submit_request_on_draft,
    link2testclient,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = draft_factory(creator.identity)
    draft1_id = draft1["id"]
    resp_request_submit = submit_request_on_draft(
        creator.identity, draft1_id, "publish_draft"
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1_id}/draft?expand=true"
    ).json
    publish = receiver_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    check_publish_topic_update(creator_client, urls, record, resp_request_submit)
