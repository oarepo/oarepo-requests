# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

from __future__ import annotations

from oarepo_requests.types import PublishDraftRequestType


def test_publish_request_payload_schema(app, db):
    ma_schema = PublishDraftRequestType.marshmallow_schema()
    assert ma_schema().dump({"payload": {"version": "v1"}}) == {
        "payload": {"version": "v1"},
        "links": {},
        "title": "Publish draft",
    }
