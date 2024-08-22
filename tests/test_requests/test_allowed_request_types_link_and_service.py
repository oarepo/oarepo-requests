from flask import current_app

from thesis.ext import ThesisExt


def test_allowed_request_types_on_service(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)

    thesis_ext: ThesisExt = current_app.extensions["thesis"]
    thesis_requests_service = thesis_ext.service_requests

    allowed_request_types = thesis_requests_service.get_applicable_request_types(
        creator.identity, draft1.json["id"]
    )
    assert allowed_request_types.to_dict() == {
        'hits': {
            'hits': [
                {
                    'links': {
                        'actions': {'create': f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'}
                    },
                    'type_id': 'publish_draft'
                }
            ],
            'total': 1,
        },
        'links': {
            'self': f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/applicable'
        }
    }



def test_allowed_request_types_on_resource(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]
    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)

    applicable_requests_link = draft1.json["links"]["applicable-requests"]
    allowed_request_types = creator_client.get(applicable_requests_link)
    assert allowed_request_types.json == {
        'hits': {
            'hits': [
                {
                    'links': {
                        'actions': {'create': f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/publish_draft'}
                    },
                    'type_id': 'publish_draft'
                }
            ],
            'total': 1,
        },
        'links': {
            'self': f'https://127.0.0.1:5000/api/thesis/{draft1.json["id"]}/draft/requests/applicable'
        }
    }