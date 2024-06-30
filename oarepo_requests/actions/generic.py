from invenio_requests.customizations import actions
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from oarepo_workflows.proxies import current_oarepo_workflows

from oarepo_requests.permissions.identity import RequestIdentity, request_active
from oarepo_requests.utils import get_from_requests_workflow, get_matching_service_for_record
from invenio_records_resources.services.uow import RecordCommitOp



def _try_state_change(identity, action, action_name, request_states, topic, uow, *args, **kwargs):
    if topic.model.is_deleted: #todo should status be changed on deleted topic too?
        return
    if action_name in request_states:
        revision_before = topic.revision_id
        current_oarepo_workflows.set_state(identity, topic, request_states[action_name], request=action.request, uow=uow)
        service = get_matching_service_for_record(topic)
        record_cls = service.draft_cls if topic.is_draft else service.record_cls
        updated_topic = record_cls.pid.resolve(topic["id"], registered_only=False) if topic.is_draft else record_cls.pid.resolve(topic.id)
        # todo discuss this - topic can be updated within set_state - for example due to autocreation of another request
        # ie. accept action of approve triggers autocreation of publish request, switching the state to publishing
        if revision_before == updated_topic.revision_id:
        #if revision_before == topic.revision_id:
            uow.register(RecordCommitOp(topic, indexer=service.indexer))
"""
class TopicStateChangeFromWorkflowMixin:
    def _try_state_change(self, identity, action, request_states, topic, uow, *args, **kwargs):
        if action in request_states:
            revision_before = topic.revision_id
            current_oarepo_workflows.set_state(identity, topic, request_states[action], request=self.request, uow=uow)
            service = get_matching_service_for_record(topic)
            record_cls = service.draft_cls if topic.is_draft else service.record_cls
            updated_topic = record_cls.pid.resolve(topic["id"], registered_only=False) if topic.is_draft else record_cls.pid.resolve(topic.id)
            # todo discuss this - topic can be updated within set_state - for example due to autocreation of another request
            # ie. accept action of approve triggers autocreation of publish request, switching the state to publishing
            if revision_before == updated_topic.revision_id:
                uow.register(RecordCommitOp(topic, indexer=service.indexer))

    def execute(self, identity, uow, *args, **kwargs):
        super().execute(identity, uow, *args, **kwargs)
        topic = self.request.topic.resolve()
        request_type = self.request.type.type_id
        workflow_id = getattr(topic.parent, "workflow", None)
        request_states = get_from_requests_workflow(workflow_id, request_type, "transitions")
#        for action in STATE_CHANGING_ACTIONS:
        self._try_state_change(identity, self.action, request_states, topic, uow)

class RequestIdentityActionMixin:
    def execute(self, identity, *args, **kwargs):
        identity = RequestIdentity(identity)
        super().execute(identity, *args, **kwargs)
"""

#----
class RequestIdentityComponent:
    def before(self, action, identity, uow, *args, **kwargs):
        identity.provides.add(request_active)

    def after(self, action, identity, uow, *args, **kwargs):
        if request_active in identity.provides:
            identity.provides.remove(request_active)

class TopicStateChangeFromWorkflowComponent:
    def before(self, action, identity, uow, *args, **kwargs):
        pass
    def after(self, action, identity, uow, *args, **kwargs):
        topic = action.request.topic.resolve()
        request_type = action.request.type.type_id
        workflow_id = getattr(topic.parent, "workflow", None)
        request_states = get_from_requests_workflow(workflow_id, request_type, "transitions")
        _try_state_change(identity, action, action.action_type, request_states, topic, uow, *args, **kwargs)

#----
class OARepoGenericActionMixin:
    #todo alternatively this can be abstract methods or mixins instead of components
    components = []
    action = None

    def execute(self, identity, uow, *args, **kwargs):

        for c in self.components:
            c.before(self, identity, uow, *args, **kwargs)
        if self.action:
            self.action(identity, uow, *args, **kwargs)
        super().execute(identity, uow, *args, **kwargs)
        for c in self.components:
            c.after(self, identity, uow, *args, **kwargs)

class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    action_type = "submit"
    components = [TopicStateChangeFromWorkflowComponent(), RequestIdentityComponent()]

class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    action_type = "decline"
    components = [TopicStateChangeFromWorkflowComponent(), RequestIdentityComponent()]

class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    action_type = "accept"
    components = [TopicStateChangeFromWorkflowComponent(), RequestIdentityComponent()]

#----


"""
class TopicStateChangingSubmitAction(TopicStateChangeFromWorkflowMixin, actions.SubmitAction):
    action = "submit"

class StatusChangingCreateAndSubmitAction(TopicStateChangeFromWorkflowMixin, actions.CreateAndSubmitAction):
    action = "create"

class StatusChangingAcceptAction(TopicStateChangeFromWorkflowMixin, actions.AcceptAction):
    action = "accept"

class TopicStateChangingDeclineAction(TopicStateChangeFromWorkflowMixin, actions.DeclineAction):
    action = "decline"
"""

class AutoAcceptSubmitAction(actions.SubmitAction):
    log_event = True

    def execute(self, identity, uow):
        super().execute(identity, uow)
        action_obj = RequestActions.get_action(self.request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow)
