#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-ui (see https://github.com/oarepo/oarepo-ui).
#
# oarepo-ui is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo Requests module initialization.

This module provides the main entry point for the OARepo Requests extension
of Invenio which adds better handling of requests.
"""

from __future__ import annotations

from .ext import OARepoRequests

__version__ = "3.0.0"

__all__ = [
    "OARepoRequests",
    "__version__",
]