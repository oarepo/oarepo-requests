#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#


from __future__ import annotations

from invenio_access.permissions import system_identity
from invenio_search.engine import dsl


def test_search_by_topic_model_type(
    requests_model,
    users,
    record_service,
    default_record_with_workflow_json,
    search_clear,
):
    from invenio_requests.proxies import current_requests_service

    creator = users[0]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    current_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,  # noqa SLF001
        expand=True,
    )
    assert (
        len(current_requests_service.search(system_identity, extra_filter=dsl.Q("exists", field="topic.requests_test")))
        == 1
    )


def test_model_topic_reference_popped(
    requests_model,
    users,
    record_service,
    default_record_with_workflow_json,
    search_clear,
):
    from invenio_requests.proxies import current_requests_service

    creator = users[0]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    current_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,  # noqa SLF001
        expand=True,
    )
    search = current_requests_service.search(system_identity)
    assert next(iter(search))["topic"] == {"record": draft.id}
