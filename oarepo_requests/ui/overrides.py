#
# Copyright (c) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more details.
#
"""UI overrides for oarepo request types.

Registers per-request-type Label and Icon React components on every page
that renders request UIs (dashboards + detail pages), via oarepo-ui's
``UIComponentOverride`` machinery.
"""

from __future__ import annotations

from oarepo_ui.overrides import UIComponent, UIComponentOverride
from oarepo_ui.proxies import current_ui_overrides

_LABELS_PATH = "@js/oarepo_requests/components/labels"
_ICONS_PATH = "@js/oarepo_requests/components/icons"

# request type_id -> exported JS component name in labels.js
REQUEST_TYPE_LABELS: dict[str, str] = {
    "publish_draft": "LabelTypePublishDraft",
    "new_version": "LabelTypeNewVersion",
    "publish_new_version": "LabelTypePublishNewVersion",
    "publish_changed_metadata": "LabelTypePublishChangedMetadata",
    "delete_published_record": "LabelTypeDeletePublishedRecord",
    "edit_published_record": "LabelTypeEditPublishedRecord",
}

# request type_id -> exported JS component name in icons.js
REQUEST_TYPE_ICONS: dict[str, str] = {
    "publish_draft": "IconTypePublishDraft",
    "new_version": "IconTypeNewVersion",
    "publish_new_version": "IconTypePublishNewVersion",
    "publish_changed_metadata": "IconTypePublishChangedMetadata",
    "delete_published_record": "IconTypeDeletePublishedRecord",
    "edit_published_record": "IconTypeEditPublishedRecord",
}

# Every Flask blueprint endpoint whose page renders RequestTypeLabel /
# RequestTypeIcon for a request whose type_id may be one of ours. Add to
# this tuple as new request UI pages appear in the repo.
REQUESTS_UI_ENDPOINTS: tuple[str, ...] = (
    "invenio_app_rdm_users.requests",
    "invenio_communities.communities_requests",
    "invenio_app_rdm_requests.user_dashboard_request_view",
    "invenio_app_rdm_requests.community_dashboard_request_view",
    "invenio_app_rdm_requests.community_dashboard_invitation_view",
    "invenio_app_rdm_requests.community_dashboard_membership_request_view",
)


def register_request_ui_overrides() -> None:
    """Register Label + Icon overrides for every oarepo request type on every page."""
    label_components = {type_id: UIComponent(name, _LABELS_PATH) for type_id, name in REQUEST_TYPE_LABELS.items()}
    icon_components = {type_id: UIComponent(name, _ICONS_PATH) for type_id, name in REQUEST_TYPE_ICONS.items()}

    for endpoint in REQUESTS_UI_ENDPOINTS:
        for type_id, component in label_components.items():
            current_ui_overrides.add(UIComponentOverride(endpoint, f"RequestTypeLabel.layout.{type_id}", component))
        for type_id, component in icon_components.items():
            current_ui_overrides.add(
                UIComponentOverride(
                    endpoint,
                    f"InvenioRequests.RequestTypeIcon.layout.{type_id}",
                    component,
                )
            )
