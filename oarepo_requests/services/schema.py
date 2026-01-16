#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Enhancements to the request schema."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any

import marshmallow as ma
from invenio_drafts_resources.records.api import Record
from invenio_records_resources.services.base.links import (
    EndpointLink,
    LinksTemplate,
)
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields

from oarepo_requests.utils import ref_to_str, reference_entity
from oarepo_requests.ext import current_request_type_registry

request_type_identity_ctx: ContextVar[Any] = ContextVar(
    "oarepo_requests.request_type_identity", default=None
)
request_type_record_ctx: ContextVar[Any] = ContextVar(
    "oarepo_requests.request_type_record", default=None
)


def get_links_schema() -> ma.fields.Dict:
    """Get links schema."""
    return ma.fields.Dict(
        keys=ma.fields.String()
    )  # value is either string or dict of strings (for actions)


class RequestTypeSchema(ma.Schema):
    """Request type schema."""

    type_id = ma.fields.String()
    """Type ID of the request type."""

    links = get_links_schema()
    """Links to the request type."""

    @ma.post_dump
    def _create_link(self, data: dict, **kwargs: Any) -> dict:  # noqa ARG002
        if "links" in data:
            return data
        type_id = data["type_id"]
        identity = request_type_identity_ctx.get()
        record = request_type_record_ctx.get()
        topic_ref = ref_to_str(
            reference_entity(record) if isinstance(record, Record) else record
        )
        link = EndpointLink("requests.create_via_url", params=["topic", "request_type"])

        # Get request type object to check conditions
        type_obj = current_request_type_registry.lookup(type_id, quiet=True)

        # Build links dictionary starting with create
        links_dict = {"create": link}

        # Add "save" link when request has custom fields UI and is editable
        has_custom_fields_ui = (
            type_obj and hasattr(type_obj, "form") and type_obj.form is not None
        )
        is_editable = (
            type_obj and hasattr(type_obj, "is_editable") and type_obj.is_editable
        )

        if has_custom_fields_ui and is_editable:
            links_dict["save"] = link  # Same endpoint, different action

        links_dict["submit"] = link  # Always add submit link
        template = LinksTemplate(
            links_dict, context={"topic": topic_ref, "request_type": type_id}
        )
        data["links"] = {"actions": template.expand(identity, record)}
        return data

    @ma.post_dump
    def _add_type_details(self, data: dict, **kwargs: Any) -> dict:
        """Serialize details from request type."""
        type = data["type_id"]
        type_obj = current_request_type_registry.lookup(type, quiet=True)
        if hasattr(type_obj, "description"):
            data["description"] = type_obj.description
        if hasattr(type_obj, "name"):
            data["name"] = type_obj.name
        if hasattr(type_obj, "dangerous"):
            data["dangerous"] = type_obj.dangerous
        if hasattr(type_obj, "is_editable"):
            data["editable"] = type_obj.is_editable
        if hasattr(type_obj, "has_form"):
            data["has_form"] = type_obj.has_form

        # if hasattr(type_obj, "stateful_name"):
        #     data["stateful_name"] = type_obj.stateful_name(
        #         identity=self.context["identity"], topic=self.context["topic"]
        #     )
        # if hasattr(type_obj, "stateful_description"):
        #     data["stateful_description"] = type_obj.stateful_description(
        #         identity=self.context["identity"], topic=self.context["topic"]
        #     )
        return data


class NoReceiverAllowedGenericRequestSchema(GenericRequestSchema):
    """A mixin that allows serialization of requests without a receiver."""

    receiver = fields.Dict(allow_none=True)


class RequestsSchemaMixin:
    """A mixin that allows serialization of requests together with their request type."""

    requests = ma.fields.List(ma.fields.Nested(NoReceiverAllowedGenericRequestSchema))
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
