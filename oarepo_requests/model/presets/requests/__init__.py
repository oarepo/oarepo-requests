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

from oarepo_requests.model.presets.requests.blueprints.request_types.api_blueprint import ApiRequestTypesBlueprintPreset
from oarepo_requests.model.presets.requests.blueprints.requests.api_blueprint import ApiRequestsBlueprintPreset
from oarepo_requests.model.presets.requests.ext_request_types import ExtRequestTypesPreset
from oarepo_requests.model.presets.requests.ext_requests import ExtRequestsPreset
from oarepo_requests.model.presets.requests.finalize_app import RequestsFinalizeAppPreset
from oarepo_requests.model.presets.requests.records.entity_resolvers.draft_resolver import DraftResolverPreset
from oarepo_requests.model.presets.requests.records.entity_resolvers.resolver import RecordResolverPreset
from oarepo_requests.model.presets.requests.records.metadata_mapping import RequestsMetadataMappingPreset
from oarepo_requests.model.presets.requests.services.records.results import RequestsRecordItemPreset
from oarepo_requests.model.presets.requests.services.records.service_config import RequestsServiceConfigPreset

# Collection of all request-related presets in proper initialization order
requests_presets = [
    RequestsMetadataMappingPreset,  # Configure metadata mapping for requests
    ApiRequestTypesBlueprintPreset,  # Set up API blueprint for request types
    ApiRequestsBlueprintPreset,  # Set up API blueprint for requests
    RecordResolverPreset,  # Configure record entity resolver
    RequestsServiceConfigPreset,  # Configure service with request components
    RequestsRecordItemPreset,  # Configure record item results
    DraftResolverPreset,  # Configure draft entity resolver
    ExtRequestTypesPreset,  # Configure request types extension
    ExtRequestsPreset,  # Configure requests extension
    RequestsFinalizeAppPreset,  # Final application setup
]
