#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Permission generators."""

from .active import RequestActive
from .conditional import (
    IfEventOnRequestType,
    IfEventType,
    IfNoEditDraft,
    IfNoNewVersionDraft,
    IfRequestedBy,
    IfRequestType,
    IfRequestTypeBase,
)
from .workflow_based import (
    EventCreatorsFromWorkflow,
    RequestCreatorsFromWorkflow,
    RequestPolicyWorkflowCreators,
)

__all__ = (
    "RequestActive",
    "IfEventOnRequestType",
    "IfRequestType",
    "IfEventType",
    "IfRequestedBy",
    "IfRequestTypeBase",
    "IfNoEditDraft",
    "IfNoNewVersionDraft",
    "EventCreatorsFromWorkflow",
    "RequestCreatorsFromWorkflow",
    "RequestPolicyWorkflowCreators",
)
