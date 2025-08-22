from oarepo_requests.proxies import current_oarepo_requests
from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests_service

import logging


def test_publish_with_system_identity(
    app, requests_model, draft_factory, submit_request_on_draft, caplog
):
    caplog.set_level(logging.ERROR)

    mail = app.extensions.get("mail")
    assert mail

    with mail.record_messages() as outbox:

        draft1 = draft_factory(system_identity, custom_workflow="system_identity")
        draft1_id = draft1["id"]
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        resp_request_submit = submit_request_on_draft(
            system_identity, draft1_id, "publish_draft"
        )
        assert resp_request_submit._record.created_by.reference_dict == {
            "user": "system"
        }
        assert resp_request_submit._record.receiver.reference_dict == {"user": "system"}
        requests_model.Record.index.refresh()
        requests_model.Draft.index.refresh()

        submit_response = current_requests_service.execute_action(
            system_identity,
            id_=resp_request_submit["id"],
            action="accept",
        )

        # check notification ...
        assert len(outbox) == 0

    # check that no error/exception was logged
    print(caplog.text)
    assert len(caplog.records) == 0
