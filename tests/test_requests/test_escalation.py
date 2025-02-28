# SONARQUBE-SKIP
import time

from oarepo_requests.services.escalation import check_escalations
from invenio_db import db
from invenio_requests.records.models import RequestEventModel

def test_escalate_request_most_recent(
    app, more_users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    mail = app.extensions.get("mail")
    assert mail

    creator = more_users[0]
    receiver = more_users[1]

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

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()

        # nothing should change, first escalation period is 2 seconds
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '2'}
        assert len(outbox) == 0

    # wait until escalation time, should take the most recent
    time.sleep(3)

    with mail.record_messages() as outbox:
        check_escalations()

        # check again
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '3'}

        # event should exist in DB
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()
        assert len(results) == 1

        # check sent mail
        assert len(outbox) == 1
        assert outbox[-1].body.endswith("Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user3@example.org"

def test_escalate_request_most_recent_multiple_recipients(
    app, more_users, record_service, default_record_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service
    mail = app.extensions.get("mail")
    assert mail

    record_multiple_recipients = {
        **default_record_json,
        "parent": {"workflow": "multiple_recipients"},
    }

    creator = more_users[0]
    receiver = more_users[1]
    draft = record_service.create(creator.identity, record_multiple_recipients)
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
    assert request.data['receiver'] == {'multiple': '[{"user": "2"}, {"user": "1"}, {"user": "10"}]'}

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()
        assert len(outbox) == 0 # nothing should be sent, escalation did not happen

    # nothing should change, first escalation period is 2 seconds
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'multiple': '[{"user": "2"}, {"user": "1"}, {"user": "10"}]'}

    # wait until escalation time, should take the most recent
    with mail.record_messages() as outbox:
        time.sleep(3)
        check_escalations()

        # check again
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'multiple': '[{"user": "3"}, {"user": "7"}]'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()
        assert len(results) == 1

def test_escalate_request_most_recent_2(
        app, more_users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service
    mail = app.extensions.get("mail")
    assert mail


    creator = more_users[0]
    receiver = more_users[1]
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

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()

        # check before escalation
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '2'}

        # wait until escalation time
        time.sleep(8)
        assert len(outbox) == 0 # escalation did not happen

    with mail.record_messages() as outbox:
        check_escalations()

        # check again
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '4'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()

        assert len(results) == 1
        assert len(outbox) == 1
        assert outbox[-1].body.endswith("Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user4@example.org"


def test_escalate_request_most_recent_2_multiple_recipients(
       app, more_users, record_service, default_record_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service
    mail = app.extensions.get("mail")
    assert mail

    creator = more_users[0]
    receiver = more_users[1]

    record_multiple_recipients = {
        **default_record_json,
        "parent": {"workflow": "multiple_recipients"},
    }


    draft = record_service.create(creator.identity, record_multiple_recipients)
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

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()
        assert len(outbox) == 0 # escalation didnt happen

    # check before escalation
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'multiple': '[{"user": "2"}, {"user": "1"}, {"user": "10"}]'}

    # wait until escalation time
    time.sleep(8)
    check_escalations()

    # check again
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'user': '4'}

    # assert event exist
    results = db.session.query(RequestEventModel).filter(
        RequestEventModel.request_id == id_,
        RequestEventModel.type == "E",
    ).all()

    assert len(results) == 1


def test_escalate_request_most_recent_3(
       app,  more_users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    mail = app.extensions.get("mail")
    assert mail

    creator = more_users[0]
    receiver = more_users[1]
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

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()

        # check before escalation
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '2'}
        assert len(outbox) == 0

    # wait until escalation time
    time.sleep(12)

    with mail.record_messages() as outbox:
        check_escalations()

        # check again
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '5'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()

        assert len(results) == 1

        assert len(outbox) == 1
        assert outbox[-1].body.endswith(
            "Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user5@example.org"


def test_escalate_request_most_recent_3_multiple_recipients(
        app, more_users, record_service, default_record_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    mail = app.extensions.get("mail")
    assert mail
    creator = more_users[0]
    receiver = more_users[1]

    record_multiple_recipients = {
        **default_record_json,
        "parent": {"workflow": "multiple_recipients"},
    }

    draft = record_service.create(creator.identity, record_multiple_recipients)
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

    with mail.record_messages() as outbox:
        # escalate
        check_escalations()
        assert len(outbox) == 0

    # check before escalation
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'multiple': '[{"user": "2"}, {"user": "1"}, {"user": "10"}]'}

    # wait until escalation time
    time.sleep(12)
    check_escalations()

    # check again
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'user': '5'}

    # assert event exist
    results = db.session.query(RequestEventModel).filter(
        RequestEventModel.request_id == id_,
        RequestEventModel.type == "E",
    ).all()

    assert len(results) == 1

def test_escalate_request_already_processed(
       app, more_users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service
    mail = app.extensions.get("mail")
    assert mail

    creator = more_users[0]
    receiver = more_users[1]
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

    # wait until escalation
    time.sleep(12)

    with mail.record_messages() as outbox:
        check_escalations()

        # check before escalation
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '5'}

        # nothing should change
        check_escalations()
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '5'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()

        assert len(results) == 1

        assert len(outbox) == 1 # only 1 sent mail
        assert outbox[-1].body.endswith(
            "Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user5@example.org"


def test_escalate_request_already_processed_multiple_recipients(
     more_users, record_service, default_record_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service

    creator = more_users[0]
    receiver = more_users[1]

    record_multiple_recipients = {
        **default_record_json,
        "parent": {"workflow": "multiple_recipients"},
    }

    draft = record_service.create(creator.identity, record_multiple_recipients)
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

    time.sleep(16)
    check_escalations()

    # check before escalation
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'multiple': '[{"user": "5"}, {"user": "6"}]'}

    # nothing should change
    check_escalations()
    request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
    assert request.data['receiver'] == {'multiple': '[{"user": "5"}, {"user": "6"}]'}


    # assert event exist
    results = db.session.query(RequestEventModel).filter(
        RequestEventModel.request_id == id_,
        RequestEventModel.type == "E",
    ).all()

    assert len(results) == 1

def test_escalate_request_already_processed_2(
       app, more_users, record_service, default_record_with_workflow_json, search_clear
):
    from invenio_requests.proxies import (
        current_requests_service as current_invenio_requests_service,
    )

    from oarepo_requests.proxies import current_oarepo_requests_service
    mail = app.extensions.get("mail")
    assert mail


    creator = more_users[0]
    receiver = more_users[1]
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

    # wait until escalation
    time.sleep(3)

    with mail.record_messages() as outbox:
        check_escalations()

        # first escalation
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '3'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()

        assert len(results) == 1

        assert len(outbox) == 1
        assert outbox[-1].body.endswith(
            "Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user3@example.org"


        # second escalation
        time.sleep(7)
        check_escalations()
        request = current_oarepo_requests_service.read(identity=creator.identity, id_=id_)
        assert request.data['receiver'] == {'user': '4'}

        # assert event exist
        results = db.session.query(RequestEventModel).filter(
            RequestEventModel.request_id == id_,
            RequestEventModel.type == "E",
        ).all()

        assert len(results) == 2
        assert len(outbox) == 2 # first escalation mail + second escalation mail
        assert outbox[-1].body.endswith(
            "Request was escalated to you since the original recipient did not approve the request in time.")
        assert outbox[-1].recipients[0] == "user4@example.org"











