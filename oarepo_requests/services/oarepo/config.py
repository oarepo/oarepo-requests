#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration for the oarepo request service."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from invenio_records_resources.services.base.links import Link
from invenio_requests.services import RequestsServiceConfig


if TYPE_CHECKING:
    from invenio_requests.records.api import Request
log = logging.getLogger(__name__)


class RedirectLink(Link):
    """..."""

    def __init__(self, when: callable | None = None):
        """Construct."""
        self._when_func = when

    def expand(self, obj: Request, context: dict) -> dict:
        """Create the request links."""
        link = None
        if "payload" in obj and "created_topic:links:self_html" in obj["payload"]:
            link = obj["payload"]["created_topic:links:self_html"]
        return link


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    """
    links_item: ClassVar[dict] = {
        "ui_redirect_url": RedirectLink(),
    }
    """
