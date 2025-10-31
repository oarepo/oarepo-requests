#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Default configuration for oarepo-requests to be initialized at invenio_config.module entrypoint."""

from __future__ import annotations

from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig
from oarepo_requests.services.oarepo.service import OARepoRequestsService

REQUESTS_SERVICE_CLASS = OARepoRequestsService
REQUESTS_SERVICE_CONFIG_CLASS = OARepoRequestsServiceConfig

REQUESTS_RESOURCE_CLASS = OARepoRequestsResource
REQUESTS_RESOURCE_CONFIG_CLASS = OARepoRequestsResourceConfig
