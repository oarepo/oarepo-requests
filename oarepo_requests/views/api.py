#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""API views."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Blueprint, Flask


# TODO: override_invenio_requests_config
def create_oarepo_requests(app: Flask) -> Blueprint:
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    return ext.requests_resource.as_blueprint()

    # notification patches need to be added separately because this part
    # is not called in celery. See app.py which is called in celery
