#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration of the draft record requests resource."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Union

from flask import g
from flask_resources import (
    HTTPJSONException,
    create_error_handler,
)
from flask_resources.serializers.json import JSONEncoder
from oarepo_communities.errors import (
    CommunityAlreadyIncludedException,
    TargetCommunityNotProvidedException,
)
from oarepo_runtime.i18n import lazy_gettext as _

from oarepo_requests.resources.record.config import RecordRequestsResourceConfig


class CustomHTTPJSONException(HTTPJSONException):
    """Custom HTTP Exception delivering JSON error responses with an error_type."""

    def __init__(
        self,
        code: Optional[int] = None,
        errors: Optional[Union[dict[str, any], list]] = None,
        error_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize CustomHTTPJSONException."""
        super().__init__(code=code, errors=errors, **kwargs)
        self.error_type = error_type  # Save the error_type passed in the constructor

    def get_body(self, environ: any = None, scope: any = None) -> str:
        """Get the request body."""
        body = {"status": self.code, "message": self.get_description(environ)}

        errors = self.get_errors()
        if errors:
            body["errors"] = errors

        # Add error_type to the response body
        if self.error_type:
            body["error_type"] = self.error_type

        # TODO: Revisit how to integrate error monitoring services. See issue #56
        # Temporarily kept for expediency and backward-compatibility
        if self.code and (self.code >= 500) and hasattr(g, "sentry_event_id"):
            body["error_id"] = str(g.sentry_event_id)

        return json.dumps(body, cls=JSONEncoder)


class DraftRecordRequestsResourceConfig(RecordRequestsResourceConfig):
    """Configuration of the draft record requests resource."""

    routes = {
        **RecordRequestsResourceConfig.routes,
        "list-requests-draft": "/<pid_value>/draft/requests",
        "request-type-draft": "/<pid_value>/draft/requests/<request_type>",
    }

    error_handlers = {
        CommunityAlreadyIncludedException: create_error_handler(
            lambda e: CustomHTTPJSONException(
                code=400,
                description="The community is already included in the record.",
                errors=[
                    {
                        "field": "payload.community",
                        "messages": [
                            _("This is already a primary community of this record.")
                        ],
                    }
                ],
                error_type="cf_validation_error",
            )
        ),
        TargetCommunityNotProvidedException: create_error_handler(
            lambda e: CustomHTTPJSONException(
                code=400,
                description="Target community not provided in the migration request.",
                errors=[
                    {
                        "field": "payload.community",
                        "messages": [_("Target community is a required field.")],
                    }
                ],
                error_type="cf_validation_error",
            )
        ),
    }
