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


def test_crash_on_submit(
    requests_model,
    users,
    urls,
    record_factory,
    create_request_on_record,
    search_clear,
):
    creator = users[0]

    record1 = record_factory(creator.identity, custom_workflow="edit_accept_crash")
    id_ = record1["id"]
    request = create_request_on_record(creator.identity, id_, "edit_published_record")
    with pytest.raises(PermissionDeniedError, match="edit"):
        current_requests_service.execute_action(creator.identity, request["id"], "submit")

    request = current_requests_service.read(system_identity, request["id"])
    assert request.data["status"] == "created"
