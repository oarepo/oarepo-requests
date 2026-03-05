#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Proxy objects for accessing the current application's requests service and resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from invenio_requests.proxies import (
    current_requests_service as current_invenio_requests_service,
)
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from oarepo_requests.ext import _OARepoRequestsState
    from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource
    from oarepo_requests.services.oarepo.service import OARepoRequestsService

current_oarepo_requests: _OARepoRequestsState = LocalProxy(  # type: ignore[assignment]
    lambda: current_app.extensions["oarepo-requests"]
)
current_requests_service: OARepoRequestsService = current_invenio_requests_service  # type: ignore[assignment]
current_oarepo_requests_resource: OARepoRequestsResource = LocalProxy(  # type: ignore[assignment]
    lambda: current_app.extensions["oarepo-requests"].requests_resource
)

current_notification_recipient_generators_registry = LocalProxy(  # type: ignore[assignment]
    lambda: current_app.extensions["oarepo-requests"].notification_recipients_resolvers_registry
)
