"""Blueprints for the app and events views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

if TYPE_CHECKING:
    from flask import Flask


def create_app_blueprint(app: Flask) -> Blueprint:
    """Create a blueprint for the requests endpoint.

    :param app: Flask application
    """
    blueprint = Blueprint("oarepo_requests_app", __name__, url_prefix="/requests/")
    return blueprint


def create_app_events_blueprint(app: Flask) -> Blueprint:
    """Create a blueprint for the requests events endpoint.

    :param app: Flask application
    """
    blueprint = Blueprint(
        "oarepo_requests_events_app", __name__, url_prefix="/requests/"
    )
    return blueprint
