
from oarepo_requests.utils import get_matching_service_for_refdict


def fallback_label_result(reference):
    id_ = list(reference.values())[0]
    return f"id: {id_}"


def fallback_result(reference):
    type = list(reference.keys())[0]
    return {
        "reference": reference,
        "type": type,
        "label": fallback_label_result(reference),
    }


def user_entity_reference_ui_resolver(identity, data, ctx):
    # return fallback_result(reference)

    reference = data["reference"]
    ref_key = list(reference.keys())[0]
    id = reference["user"]

    by_id = [
        resolved for resolved in ctx["resolved"][ref_key] if resolved.data["id"] == id
    ]
    if not by_id:
        return fallback_result(reference)
    record = by_id[0]

    """
    try:
        record = current_users_service.read(identity, user_id)
    except PermissionDeniedError:
        return fallback_result(reference)
    """
    if record.data["username"] is None:  # username undefined?
        if "email" in record.data:
            label = record.data["email"]
        else:
            label = fallback_label_result(reference)
    else:
        label = record.data["username"]
    ret = {
        "reference": reference,
        "type": "user",
        "label": label,
    }
    if "links" in record.data and "self" in record.data["links"]:
        ret["link"] = record.data["links"]["self"]
    return ret


def _record_entity_reference_ui_resolver_inner(identity, data, ctx, is_draft):
    reference = data["reference"]
    ref_key = list(reference.keys())[0]
    id = list(reference.values())[0]
    service = get_matching_service_for_refdict(reference)

    reader = service.read_draft if is_draft else service.read
    """
    try:
        response = reader(identity, id)
    except PermissionDeniedError:
        return fallback_result(reference)
        record = response.data
    """
    by_id = [resolved for resolved in ctx["resolved"][ref_key] if resolved["id"] == id]
    if not by_id:
        return fallback_result(reference)
    record = by_id[0]

    if "metadata" in record and "title" in record["metadata"]:
        label = record["metadata"]["title"]
    else:
        label = fallback_label_result(reference)
    ret = {
        "reference": reference,
        "type": list(reference.keys())[0],
        "label": label,
        "link": record["links"]["self"],
    }
    return ret


def fallback_entity_reference_ui_resolver(identity, data, ctx):
    reference = data["reference"]
    id = list(reference.values())[0]
    try:
        service = get_matching_service_for_refdict(reference)
    except:
        return fallback_result(reference)
    try:
        response = service.read(identity, id)
    except:
        try:
            response = service.read_draft(identity, id)
        except:
            return fallback_result(reference)

    record = response.data
    if "metadata" in record and "title" in record["metadata"]:
        label = record["metadata"]["title"]
    else:
        label = fallback_label_result(reference)

    ret = {"reference": reference, "type": list(reference.keys())[0], "label": label}
    if "links" in record and "self" in record["links"]:
        ret["link"] = record["links"]["self"]
    return ret


def record_entity_reference_ui_resolver(identity, data, ctx):
    return _record_entity_reference_ui_resolver_inner(
        identity, data, ctx, is_draft=False
    )


def draft_record_entity_reference_ui_resolver(identity, data, ctx):
    return _record_entity_reference_ui_resolver_inner(
        identity, data, ctx, is_draft=True
    )
