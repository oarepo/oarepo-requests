#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Blueprints for the app and events views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask


def create_app_blueprint(app: Flask) -> Blueprint:  # noqa ARG001
    """Create a blueprint for the requests endpoint.

    :param app: Flask application
    """
    return Blueprint("oarepo_requests_app", __name__, url_prefix="/requests/")
