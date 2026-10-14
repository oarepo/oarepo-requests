# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

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
]
