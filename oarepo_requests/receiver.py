from oarepo_requests.errors import RequestTypeNotInWorkflow, ReceiverUnreferencable


def default_workflow_receiver_function(record=None, request_type=None, **kwargs):
    from oarepo_workflows.proxies import current_oarepo_workflows

    workflow_id = current_oarepo_workflows.get_workflow_from_record(record)
    if not workflow_id:
        return None #exception?

    try:

        request = getattr(
            current_oarepo_workflows.record_workflows[workflow_id].requests(),
            request_type.type_id,
        )
    except AttributeError:
        raise RequestTypeNotInWorkflow(request_type.type_id, workflow_id)

    receiver = request.reference_receivers(
        record=record, request_type=request_type, **kwargs
    )
    if not request_type.receiver_can_be_none and not receiver:
        raise ReceiverUnreferencable(request_type=request_type)
    return receiver
