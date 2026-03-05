#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""UI components."""

from __future__ import annotations

from oarepo_requests.ui.components.action_labels import ActionLabelsComponent
from oarepo_requests.ui.components.custom_fields import (
    FormConfigCustomFieldsComponent,
    FormConfigRequestTypePropertiesComponent,
)
from oarepo_requests.ui.components.ui_config import RequestsUIConfigComponent

__all__ = (
    "ActionLabelsComponent",
    "FormConfigCustomFieldsComponent",
    "FormConfigRequestTypePropertiesComponent",
    "RequestsUIConfigComponent",
)
