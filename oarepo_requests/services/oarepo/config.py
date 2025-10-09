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

from invenio_requests.services import RequestsServiceConfig

from oarepo_requests.services.search import EnhancedRequestSearchOptions

log = logging.getLogger(__name__)


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    search = EnhancedRequestSearchOptions
