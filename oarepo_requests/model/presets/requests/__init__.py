#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see http://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""OARepo requests model presets.

This module provides a collection of presets for configuring requests functionality
in OARepo models. The presets include components for API blueprints, service configurations,
entity resolvers, metadata mappings, and application finalization.

The requests_presets list contains all available presets in the correct order for
application during model building.
"""

from __future__ import annotations

from oarepo_requests.model.presets.requests.records.metadata_mapping import (
    RequestsMetadataMappingPreset,
)
from oarepo_requests.model.presets.requests.register_resolvers import (
    RegisterResolversPreset,
)
from oarepo_requests.model.presets.requests.services.records.results import (
    RequestsRecordItemPreset,
)
from oarepo_requests.model.presets.requests.services.records.service_config import (
    RequestsServiceConfigPreset,
)

# Collection of all request-related presets in proper initialization order
requests_preset = [
    RequestsMetadataMappingPreset,  # Configure metadata mapping for requests
    RequestsServiceConfigPreset,  # Configure service with request components
    RequestsRecordItemPreset,  # Configure record item results
    RegisterResolversPreset,  # Final application setup
]
