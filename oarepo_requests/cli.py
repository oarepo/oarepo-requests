from oarepo_runtime.cli import oarepo
from oarepo_requests.services.escalation import check_escalations

@oarepo.group(name='requests')
def oarepo_requests():
    pass

@oarepo_requests.command(name='escalate')
def escalate_requests():
    check_escalations()