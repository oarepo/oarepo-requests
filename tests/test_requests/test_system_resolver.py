#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

import logging

from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests_service


def test_publish_with_system_identity(app, requests_model, draft_factory, submit_request_on_draft, caplog):
    caplog.set_level(logging.ERROR)

    mail = app.extensions.get("mail")
    assert mail

    with mail.record_messages() as outbox:
        draft1 = draft_factory(system_identity, custom_workflow="system_identity")
        draft1_id = draft1["id"]
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        resp_request_submit = submit_request_on_draft(system_identity, draft1_id, "publish_draft")
        assert resp_request_submit._record.created_by.reference_dict == {"user": "system"}
        assert resp_request_submit._record.receiver.reference_dict == {"user": "system"}
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        current_requests_service.execute_action(
            system_identity,
            id_=resp_request_submit["id"],
            action="accept",
        )

        # check notification ...
        assert len(outbox) == 0

    # check that no error/exception was logged
    assert len(caplog.records) == 0
