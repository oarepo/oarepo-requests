#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-communities).
#
# oarepo-communities is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Notifications entity resolvers."""

from __future__ import annotations

from typing import Any, override

from invenio_records.dumpers import SearchDumperExt

from oarepo_requests.utils import resolve_reference_dict


class RecordReferenceDumperExt(SearchDumperExt):
    """Dumper for a adding reference to record type to topic."""

    @override
    def dump(self, record: Any, data: dict[str, Any]) -> None:
        """Add the record type reference."""
        if "record" in data["topic"]:
            topic = resolve_reference_dict(record["topic"])
            model_type = topic.parent.model.model
            record_id = data["topic"]["record"]
            data["topic"] = [{"record": record_id}, {model_type: record_id}]
        else:
            data["topic"] = [data["topic"]]

    @override
    def load(self, data: dict[str, Any], record_cls: type) -> None:
        """Remove the record type reference."""
        data["topic"] = data["topic"][0]
