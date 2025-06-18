import pytest
from invenio_records_resources.services.errors import PermissionDeniedError
from oarepo_requests.proxies import current_oarepo_requests_service

def test_privileged(
    users, draft_factory, submit_request_on_draft, submit_request_on_record,
        search_clear
):

    creator = users[0]
    receiver = users[1]
    privileged_user = users[2]
    other_user = users[3]

    draft = draft_factory(creator.identity, custom_workflow="privileged_access")
    request = submit_request_on_draft(creator.identity, draft["id"], "publish_draft")

    receiver_read = current_oarepo_requests_service.read(receiver.identity, request["id"])
    privileged_read = current_oarepo_requests_service.read(privileged_user.identity, request["id"])
    with pytest.raises(PermissionDeniedError):
        other_read = current_oarepo_requests_service.read(other_user.identity, request["id"])

    #try different action doesn't work
    with pytest.raises(PermissionDeniedError):
        privileged_update = current_oarepo_requests_service.update(privileged_user.identity, request["id"], request.data)

    accept = current_oarepo_requests_service.execute_action(privileged_user.identity, request["id"], "accept")

    #try it doesn't work on different request type
    with pytest.raises(PermissionDeniedError):
        privileged_delete_published = submit_request_on_record(privileged_user.identity, draft["id"],
                                                               "delete_published_record")

    privileged_delete_published = submit_request_on_record(creator.identity, draft["id"], "delete_published_record")

"""
# todo implementation requires searchable topic workflow
def test_search(
    users, draft_factory, submit_request_on_draft, default_record_with_workflow_json, search_clear
):

    creator = users[0]
    receiver = users[1]
    privileged_user = users[2]
    other_user = users[3]

    draft = draft_factory(creator.identity, custom_workflow="privileged_access")
    request = submit_request_on_draft(creator.identity, draft["id"], "publish_draft")

    receiver_search = current_oarepo_requests_service.search(receiver.identity)
    privileged_search = current_oarepo_requests_service.search(privileged_user.identity)
    other_search = current_oarepo_requests_service.search(other_user.identity)

    assert len(list(receiver_search.hits)) == 1
    assert len(list(privileged_search.hits)) == 1
    assert len(list(other_search.hits)) == 0
"""


