# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Configuration for the oarepo request service."""

from __future__ import annotations

import logging

from invenio_requests.services import RequestsServiceConfig

from oarepo_requests.services.search import EnhancedRequestSearchOptions

log = logging.getLogger(__name__)


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    search = EnhancedRequestSearchOptions
