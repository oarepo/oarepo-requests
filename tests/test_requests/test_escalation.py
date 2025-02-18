import time

from oarepo_requests.services.escalation import check_escalations


def test_escalate_request(
    users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    creator = users[0]
    receiver = users[1]
    draft = record_service.create(creator.identity, default_record_with_workflow_json)
    request = current_oarepo_requests_service.create(
        identity=creator.identity,
        data={"payload": {"version": "1.0"}},
        request_type="publish_draft",
        topic=draft._record,
    )
    submit_result = current_invenio_requests_service.execute_action(
        creator.identity, request.id, "submit"
    )
    id_ = request.id

    # check before escalation
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'user': '2'}

    # wait until escalation period
    time.sleep(5)
    check_escalations()

    # check again
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] != {'user': '2'}
    assert request.data['receiver'] == {'user': '4'}
