#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Errors raised by oarepo-requests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional, Union

from flask import g
from flask_resources import (
    HTTPJSONException,
)
from flask_resources.serializers.json import JSONEncoder
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_workflows.errors import (
    EventTypeNotInWorkflow as WorkflowEventTypeNotInWorkflow,
)
from oarepo_workflows.errors import (
    RequestTypeNotInWorkflow as WorkflowRequestTypeNotInWorkflow,
)
from typing_extensions import deprecated

if TYPE_CHECKING:
    from invenio_records_resources.records import Record
    from invenio_requests.customizations import RequestType


@deprecated(
    "This exception is deprecated. Use oarepo_workflows.errors.RequestTypeNotInWorkflow instead."
)
class EventTypeNotInWorkflow(WorkflowEventTypeNotInWorkflow):
    """Raised when an event type is not in the workflow."""

    ...


@deprecated(
    "This exception is deprecated. Use oarepo_workflows.errors.RequestTypeNotInWorkflow instead."
)
class RequestTypeNotInWorkflow(WorkflowRequestTypeNotInWorkflow):
    """Raised when a request type is not in the workflow."""

    ...


class CustomHTTPJSONException(HTTPJSONException):
    """Custom HTTP Exception delivering JSON error responses with an error_type."""

    def __init__(
        self,
        code: Optional[int] = None,
        errors: Optional[Union[dict[str, any], list]] = None,
        topic_errors: Optional[Union[dict[str, any], list]] = None,
        request_payload_errors: Optional[Union[dict[str, any], list]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CustomHTTPJSONException."""
        super().__init__(code=code, errors=errors, **kwargs)
        self.topic_errors = topic_errors or []
        self.request_payload_errors = request_payload_errors or []
        self.extra_kwargs = kwargs  # Save all kwargs

    def get_body(self, environ: any = None, scope: any = None) -> str:
        """Get the request body."""
        body = {"status": self.code, "message": self.get_description(environ)}

        errors = self.get_errors()
        if errors:
            body["errors"] = errors

        if self.topic_errors:
            body["topic_errors"] = self.topic_errors

        if self.request_payload_errors:
            body["request_payload_errors"] = self.request_payload_errors

        if self.code and (self.code >= 500) and hasattr(g, "sentry_event_id"):
            body["error_id"] = str(g.sentry_event_id)

        return json.dumps(body, cls=JSONEncoder)


class OpenRequestAlreadyExists(Exception):
    """An open request already exists."""

    def __init__(self, request_type: RequestType, record: Record) -> None:
        """Initialize the exception."""
        self.request_type = request_type
        self.record = record

    @property
    def description(self) -> str:
        """Exception's description."""
        return f"There is already an open request of {self.request_type.name} on {self.record.id}."


class UnknownRequestType(Exception):
    """Exception raised when user tries to create a request with an unknown request type."""

    def __init__(self, request_type: str) -> None:
        """Initialize the exception."""
        self.request_type = request_type

    @property
    def description(self) -> str:
        """Exception's description."""
        return f"Unknown request type {self.request_type}."


class ReceiverNonReferencable(Exception):
    """Raised when receiver is required but could not be estimated from the record/caller."""

    def __init__(
        self, request_type: RequestType, record: Record, **kwargs: Any
    ) -> None:
        """Initialize the exception."""
        self.request_type = request_type
        self.record = record
        self.kwargs = kwargs

    @property
    def description(self) -> str:
        """Exception's description."""
        message = f"Receiver for request type {self.request_type} is required but wasn't successfully referenced on record {self.record['id']}."
        if self.kwargs:
            message += "\n Additional keyword arguments:"
            message += f"\n{', '.join(self.kwargs)}"
        return message


class VersionAlreadyExists(CustomHTTPJSONException):
    """Exception raised when a version tag already exists."""

    def __init__(self) -> None:
        """Initialize the exception."""
        description = _("There is already a record version with this version tag.")
        request_payload_errors = [
            {
                "field": "payload.version",
                "messages": [
                    _(
                        "There is already a record version with this version tag. Please use a different version tag."
                    )
                ],
            }
        ]
        super().__init__(
            code=400,
            description=description,
            request_payload_errors=request_payload_errors,
        )
