#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from collections import defaultdict


def link2testclient(link, ui=False):
    base_string = "https://127.0.0.1:5000/api/" if not ui else "https://127.0.0.1:5000/"
    return link[len(base_string) - 1 :]


def _create_request(client, record_id, request_type, urls):
    applicable = client.get(
        f"{urls['BASE_URL']}{record_id}/draft/requests/applicable"
    ).json["hits"]["hits"]
    request_link = [
        type_["links"]["actions"]["create"]
        for type_ in applicable
        if type_["type_id"] == request_type
    ][0]
    ret = client.post(link2testclient(request_link))
    return ret


# from chatgpt
def dict_diff(dict1, dict2, path=""):
    ret = defaultdict(list)
    for key in dict1:
        # Construct path to current element
        if path == "":
            new_path = key
        else:
            new_path = f"{path}.{key}"

        # Check if the key is in the second dictionary
        if key not in dict2:
            ret["second dict missing"].append(
                f"{new_path}: Key missing in the second dictionary"
            )
            continue

        # If both values are dictionaries, do a recursive call
        if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            sub_result = dict_diff(dict1[key], dict2[key], new_path)
            ret.update(sub_result)
        # Check if values are the same
        elif dict1[key] != dict2[key]:
            ret["different values"].append(f"{new_path}: {dict1[key]} != {dict2[key]}")

    # Check for keys in the second dictionary but not in the first
    for key in dict2:
        if key not in dict1:
            if path == "":
                new_path = key
            else:
                new_path = f"{path}.{key}"
            ret["first dict missing"].append(
                f"{new_path}: Key missing in the first dictionary"
            )
    return ret


def is_valid_subdict(subdict, dict):
    diff = dict_diff(subdict, dict)
    return "different values" not in diff and "second dict missing" not in diff
