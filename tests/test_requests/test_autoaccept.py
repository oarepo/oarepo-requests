#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError

from oarepo_requests.proxies import current_requests_service


def test_revert_on_accept_crash(
    requests_model,
    users,
    urls,
    record_factory,
    create_request_on_record,
    search_clear,
):
    """Tests behavior when submit actions succeeds and accept action fails.

    Checks whether exception thrown on accept action trigerred by the autoaccept component rolls back both the
    submit and accept actions.
    """
    creator = users[0]

    record1 = record_factory(creator.identity, custom_workflow="edit_accept_crash")
    id_ = record1["id"]
    request = create_request_on_record(creator.identity, id_, "edit_published_record")
    with pytest.raises(PermissionDeniedError, match="edit"):
        current_requests_service.execute_action(creator.identity, request["id"], "submit")

    request = current_requests_service.read(system_identity, request["id"])
    assert request.data["status"] == "created"


def test_submit_accept_both_modify_topic(
    requests_model,
    users,
    record_service,
    urls,
    draft_factory,
    submit_request_on_draft,
    search_clear,
):
    """Test that persistence works correctly when submit and accept both modify the topic.

    Publish submit adds version to the topic metadata, check whether it's not lost when accept triggered by
    autoaccept component runs its course.
    """
    creator = users[0]
    record1 = draft_factory(creator.identity, custom_workflow="edit_accept_crash")
    id_ = record1["id"]
    submit_request_on_draft(creator.identity, id_, "publish_draft")
    published_record_item = record_service.read(users[0].identity, id_)
    assert "version" in published_record_item.data["metadata"]
