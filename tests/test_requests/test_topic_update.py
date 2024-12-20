#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

from .utils import link2testclient


def test_publish(
    logged_client,
    users,
    urls,
    create_draft_via_resource,
    check_publish_topic_update,
    submit_request_by_link,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    resp_request_submit = submit_request_by_link(
        creator_client, draft1, "publish_draft"
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    publish = receiver_client.post(
        link2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    check_publish_topic_update(creator_client, urls, record, resp_request_submit)
