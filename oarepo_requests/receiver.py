from oarepo_workflows.utils import get_workflow_from_record


def default_workflow_receiver_function(record=None, request_type=None, **kwargs):
    workflow_id = get_workflow_from_record(record)
    try:
        from oarepo_workflows.proxies import current_oarepo_workflows

        request = getattr(
            current_oarepo_workflows.record_workflows[workflow_id].requests,
            request_type.type_id,
        )
        receiver = request.reference_receivers(
            record=record, request_type=request_type, **kwargs
        )
        return receiver
    except (KeyError, AttributeError):
        return None
