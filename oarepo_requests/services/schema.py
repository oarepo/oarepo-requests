#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Enhancements to the request schema."""

from __future__ import annotations

from typing import Any

import marshmallow as ma
from invenio_drafts_resources.records.api import Record
from invenio_records_resources.services.base.links import (
    EndpointLink,
    LinksTemplate,
)
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields
from marshmallow_utils.context import context_schema

from oarepo_requests.utils import ref_to_str, reference_entity


class RequestTypeSchema(ma.Schema):
    """Request type schema."""

    type_id = ma.fields.String()
    """Type ID of the request type."""

    links = ma.fields.Dict(keys=ma.fields.String())
    """Links to the request type."""

    @ma.post_dump
    def _create_link(self, data: dict, **_kwargs: Any) -> dict:
        if "links" in data:
            return data
        type_id = data["type_id"]
        identity = context_schema.get()["identity"]
        record = context_schema.get()["record"]
        topic_ref = ref_to_str(reference_entity(record) if isinstance(record, Record) else record)
        link = EndpointLink("requests.create_via_url", params=["topic", "request_type"])
        template = LinksTemplate({"create": link}, context={"topic": topic_ref, "request_type": type_id})
        data["links"] = {"actions": template.expand(identity, record)}
        return data


class NoReceiverAllowedGenericRequestSchema(GenericRequestSchema):
    """A mixin that allows serialization of requests without a receiver."""

    receiver = fields.Dict(allow_none=True)


# REVIEW: links on request type but not on request?"
class RequestsSchemaMixin:
    """A mixin that allows serialization of requests together with their request type."""

    requests = ma.fields.List(ma.fields.Nested(NoReceiverAllowedGenericRequestSchema))
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
