# Copyright (c) 2024 CESNET
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""JS/CSS bundles for oarepo-requests."""

from __future__ import annotations  # pragma: no cover

from invenio_assets.webpack import WebpackThemeBundle  # pragma: no cover

theme = WebpackThemeBundle(  # pragma: no cover
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": {
            "entry": {},
            "dependencies": {},
            "devDependencies": {},
            "aliases": {
                "@js/oarepo_requests": "js/oarepo_requests",
            },
        }
    },
)
