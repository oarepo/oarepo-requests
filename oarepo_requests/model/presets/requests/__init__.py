from oarepo_requests.model.presets.requests.blueprints.request_types.api_blueprint import ApiRequestTypesBlueprintPreset
from oarepo_requests.model.presets.requests.blueprints.requests.api_blueprint import ApiRequestsBlueprintPreset
from oarepo_requests.model.presets.requests.ext_request_types import ExtRequestTypesPreset
from oarepo_requests.model.presets.requests.ext_requests import ExtRequestsPreset
from oarepo_requests.model.presets.requests.finalize_app import RequestsFinalizeAppPreset
from oarepo_requests.model.presets.requests.records.entity_resolvers.draft_resolver import DraftResolverPreset
from oarepo_requests.model.presets.requests.records.entity_resolvers.resolver import RecordResolverPreset
from oarepo_requests.model.presets.requests.services.records.results import RequestsRecordItemPreset
from oarepo_requests.model.presets.requests.services.records.service_config import RequestsServiceConfigPreset

requests_presets = [ApiRequestTypesBlueprintPreset, ApiRequestsBlueprintPreset, RecordResolverPreset,
                    RequestsServiceConfigPreset, RequestsRecordItemPreset, DraftResolverPreset, ExtRequestTypesPreset,
                    ExtRequestsPreset, RequestsFinalizeAppPreset]