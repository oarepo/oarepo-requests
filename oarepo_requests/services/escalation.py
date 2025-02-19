from datetime import datetime
from typing import Iterator

from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests_service
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.requests import RecipientEntityReference
from invenio_records_resources.services.uow import RecordCommitOp,unit_of_work
from invenio_requests.records import Request
from invenio_db import db


@unit_of_work()
def escalate_request(request, escalation, uow=None) -> None:
    """Escalate single request and commit the change to the database."""
    receiver = RecipientEntityReference(request=escalation)
    request.receiver = receiver
    request.commit()
    uow.register(RecordCommitOp(request))


def check_escalations() -> None:
    """Check and escalate all stale requests, if after time delta is reached."""
    for request, escalation in stale_requests():
        escalate_request(request, escalation)

def stale_requests() -> Iterator[Request]:
    """Yield all submitted requests with expired time of escalation"""
    hits = current_requests_service.scan(system_identity, params={"is_open": True})
    for hit in hits:
        r = Request.get_record(hit['id'])
        topic = r.topic.resolve()
        workflow = current_oarepo_workflows.get_workflow(topic)
        workflow_request = workflow.request_policy_cls.publish_draft

        for escalation in workflow_request.escalations:
            if escalation.after + r.created < datetime.now():
                yield r, escalation


