#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

import pytest
from invenio_access.permissions import system_identity
from oarepo_runtime.typing import record_from_result

from oarepo_requests.types.publish_base import PublishRequestType


def publish_new_version(record_service, record_id):
    draft = record_service.new_version(system_identity, record_id)
    return record_service.publish(system_identity, draft.id)


def test_never_published_draft_is_initial(draft_factory, record_service, users, search_clear):
    draft = draft_factory(users[0].identity)
    topic = record_from_result(record_service.read_draft(system_identity, draft["id"]))

    assert PublishRequestType.get_topic_type(topic) == "initial"


def test_published_record_is_published(record_factory, record_service, users, search_clear):
    record = record_factory(users[0].identity)
    topic = record_from_result(record_service.read(system_identity, record["id"]))

    assert PublishRequestType.get_topic_type(topic) == "published"


def test_unpublished_new_version_draft_is_new_version(record_factory, record_service, users, search_clear):
    record = record_factory(users[0].identity)
    topic = record_from_result(record_service.new_version(system_identity, record["id"]))

    assert PublishRequestType.get_topic_type(topic) == "new_version"


def test_edit_of_latest_version_is_metadata(record_factory, record_service, users, search_clear):
    record = record_factory(users[0].identity)
    topic = record_from_result(record_service.edit(system_identity, record["id"]))

    assert PublishRequestType.get_topic_type(topic) == "metadata"


@pytest.mark.parametrize("edited_version", [1, 2])
def test_edit_of_older_version_is_metadata(record_factory, record_service, users, search_clear, edited_version):
    first = record_factory(users[0].identity)
    second = publish_new_version(record_service, first["id"])
    publish_new_version(record_service, second.id)
    edited_id = [first["id"], second.id][edited_version - 1]
    topic = record_from_result(record_service.edit(system_identity, edited_id))

    assert PublishRequestType.get_topic_type(topic) == "metadata"


def test_topic_without_draft_support_is_rejected():
    with pytest.raises(TypeError, match="does not support drafts"):
        PublishRequestType.get_topic_type(object())
