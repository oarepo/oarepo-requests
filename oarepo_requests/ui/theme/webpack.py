#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Webpack entry points for the UI components of the module (requests components and dialogs)."""

from __future__ import annotations

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {
                "oarepo_requests_landing_page": "./js/oarepo_requests/landing_page/index.js",
                # "oarepo_requests_ui_request_detail": "./js/oarepo_requests_ui/request-detail/index.js",
                # "oarepo_requests_ui_components": "./js/oarepo_requests_ui/custom-components.js",
            },
            "dependencies": {},
            "devDependencies": {},
            "aliases": {
                "@translations/oarepo_requests": "translations/oarepo_requests",
                # "@js/oarepo_requests": "js/oarepo_requests_ui/record-requests",
                # "@js/oarepo_requests_detail": "js/oarepo_requests_ui/request-detail",
                # "@js/oarepo_requests_common": "js/oarepo_requests_ui/common",
            },
        }
    },
)
