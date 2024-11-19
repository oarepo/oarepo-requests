#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Proxy objects for accessing the current application's requests service and resource."""

from flask import current_app
from werkzeug.local import LocalProxy

current_oarepo_requests = LocalProxy(lambda: current_app.extensions["oarepo-requests"])
current_oarepo_requests_service = LocalProxy(
    lambda: current_app.extensions["oarepo-requests"].requests_service
)
current_oarepo_requests_resource = LocalProxy(
    lambda: current_app.extensions["oarepo-requests"].requests_resource
)
