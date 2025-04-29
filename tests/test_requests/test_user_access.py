#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import copy

from thesis.records.api import ThesisDraft, ThesisRecord

def test_user_access_request_is_applicable(
    logged_client,
    users,
    urls,
    submit_request_on_record,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)
    
    requester = users[1]
    requester_client = logged_client(requester)
        
    record1 = record_factory(creator.identity)
    record1_id = record1["id"]

    create_additional_data = {
        'payload': {
            "permission": "view",
            "message": "<p>please accept</p>",
        }
    }
    
    resp_request_submit = submit_request_on_record(
        requester.identity, record1_id, "request_user_access", create_additional_data=create_additional_data
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    assert request["status"] == "submitted"
    
    response = requester_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true").json
    assert 'submit' not in response['expanded']['requests'][0]['links']['actions']


def test_user_access_request_accept(
    logged_client,
    users,
    urls,
    default_record_json,
    submit_request_on_record,
    record_factory,
    search_clear,
    link2testclient
):
    creator = users[0]
    creator_client = logged_client(creator)
    
    requester = users[1]
    requester_client = logged_client(requester)
    
    additional_data = {
        "access": {
            "files": "restricted",
            "record": "public",
            "embargo": {
                "until": "",
                "active": False,
                "reason": ""
                }
        },
    }
    
    record1 = record_factory(creator.identity, additional_data=additional_data)
    record1_id = record1["id"]

    create_additional_data = {
        'payload': {
            "permission": "view",
            "message": "<p>please accept</p>",
        }
    }
    
    resp_request_submit = submit_request_on_record(
        requester.identity, record1_id, "request_user_access", create_additional_data=create_additional_data
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    
    assert request["status"] == "submitted"
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    
    record = creator_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true").json
    accept = creator_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    assert request['status'] == "accepted"
    
def test_user_access_request_cancel(
    logged_client,
    users,
    urls,
    default_record_json,
    submit_request_on_record,
    record_factory,
    search_clear,
    link2testclient
):
    creator = users[0]
    creator_client = logged_client(creator)
    
    requester = users[1]
    requester_client = logged_client(requester)
    
    additional_data = {
        "access": {
            "files": "restricted",
            "record": "public",
            "embargo": {
                "until": "",
                "active": False,
                "reason": ""
                }
        },
    }
    
    record1 = record_factory(creator.identity, additional_data=additional_data)
    record1_id = record1["id"]

    create_additional_data = {
        'payload': {
            "permission": "view",
            "message": "<p>please accept</p>",
        }
    }
    
    resp_request_submit = submit_request_on_record(
        requester.identity, record1_id, "request_user_access", create_additional_data=create_additional_data
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    
    assert request["status"] == "submitted"
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    
    record = requester_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true").json
    cancel = requester_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["cancel"]
        ),
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    assert request['status'] == "cancelled"  
    
    
    
def test_user_access_request_decline(
    logged_client,
    users,
    urls,
    default_record_json,
    submit_request_on_record,
    record_factory,
    search_clear,
    link2testclient
):
    creator = users[0]
    creator_client = logged_client(creator)
    
    requester = users[1]
    requester_client = logged_client(requester)
    
    
    record1 = record_factory(creator.identity)
    record1_id = record1["id"]

    create_additional_data = {
        'payload': {
            "permission": "view",
            "message": "<p>please accept</p>",
        }
    }
    
    resp_request_submit = submit_request_on_record(
        requester.identity, record1_id, "request_user_access", create_additional_data=create_additional_data
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    
    assert request["status"] == "submitted"
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    
    record = creator_client.get(f"{urls['BASE_URL']}{record1_id}?expand=true").json
    cancel = creator_client.post(
        link2testclient(
            record["expanded"]["requests"][0]["links"]["actions"]["decline"]
        ),
    )
    
    request = requester_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_submit["id"]}',
    ).json
    assert request['status'] == "declined"       
    


    