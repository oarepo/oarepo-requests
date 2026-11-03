# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Default workflow receiver function."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from oarepo_workflows.errors import (
    InvalidWorkflowError,
    MissingWorkflowError,
    RequestTypeNotInWorkflowError,
)

from oarepo_requests.errors import ReceiverNonReferencableError

if TYPE_CHECKING:
    from collections.abc import Mapping

    from invenio_requests.customizations.request_types import RequestType
    from oarepo_workflows import WorkflowRequest


def default_workflow_receiver_function(
    topic: Any,
    request_type: RequestType,
    **kwargs: Any,
) -> Mapping[str, str] | None:
    """Get the receiver of the request.

    This function is called by oarepo-requests when a new request is created. It should
    return the receiver of the request. The receiver is the entity that is responsible for
    accepting/declining the request.
    """
    from oarepo_workflows.proxies import current_oarepo_workflows

    try:
        workflow = current_oarepo_workflows.get_workflow(topic)
    except MissingWorkflowError, InvalidWorkflowError:
        # if the record does not have a workflow, we cannot determine the receiver
        return None

    if not workflow:
        return None

    try:
        request: WorkflowRequest = workflow.requests().requests_by_id[request_type.type_id]
    except KeyError as e:
        raise RequestTypeNotInWorkflowError(request_type.type_id, workflow.code) from e

    receiver = request.recipient_entity_reference(record=topic, request_type=request_type, **kwargs)
    if not request_type.receiver_can_be_none and not receiver:
        raise ReceiverNonReferencableError(request_type=request_type, topic=topic, **kwargs)
    return cast("Mapping[str, str]", receiver)
