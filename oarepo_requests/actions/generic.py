from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import actions
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError
from oarepo_workflows.proxies import current_oarepo_workflows
from oarepo_workflows.utils import get_from_requests_workflow

from oarepo_requests.permissions.identity import request_active
from oarepo_requests.resolvers.autoapprove import AutoApprover
from oarepo_requests.utils import get_matching_service_for_record


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


# ----
class RequestIdentityComponent:
    def before(self, action, identity, uow, *args, **kwargs):

        identity.provides.add(request_active)

    def after(self, action, identity, uow, *args, **kwargs):
        # todo what if something fails inbetween
        # todo nested calls could be a problem in future (identity is removed in subcall and supercall finishes without it)
        if request_active in identity.provides:
            identity.provides.remove(request_active)


class TopicStateChangeFromWorkflowComponent:

    # todo - is the repeated resolving of topic a perfomance hindrance?
    def _try_state_change(self,
            identity, action, transition_state, request_states, topic, uow, *args, **kwargs
    ):
        if topic.model.is_deleted:  # todo should status be changed on deleted topic too?
            return
        to_state = getattr(request_states, transition_state, None)
        if to_state:
            revision_before = topic.revision_id
            current_oarepo_workflows.set_state(
                identity,
                topic,
                to_state,
                request=action.request,
                uow=uow,
            )
            service = get_matching_service_for_record(topic)
            record_cls = service.draft_cls if topic.is_draft else service.record_cls
            updated_topic = (
                record_cls.pid.resolve(topic["id"], registered_only=False)
                if topic.is_draft
                else record_cls.pid.resolve(topic["id"])
            )
            # todo discuss this - topic can be updated within set_state - for example due to autocreation of another request
            # ie. accept action of approve triggers autocreation of publish request, switching the state to publishing
            if revision_before == updated_topic.revision_id:
                # if revision_before == topic.revision_id:
                uow.register(RecordCommitOp(topic, indexer=service.indexer))


    def before(self, action, identity, uow, *args, **kwargs):
        pass

    def after(self, action, identity, uow, *args, **kwargs):
        topic = action.request.topic.resolve()
        request_type = action.request.type.type_id
        # if workflows are defined
        workflow_id = getattr(topic.parent, "workflow", None)
        if not workflow_id:
            return
        request_states = get_from_requests_workflow(
            workflow_id, request_type, "transitions"
        )
        self._try_state_change(
            identity,
            action,
            action.transition_state,
            request_states,
            topic,
            uow,
            *args,
            **kwargs,
        )


class AutoAcceptComponent:
    def before(self, action, identity, uow, *args, **kwargs):
        pass

    def after(self, action, identity, uow, *args, **kwargs):
        if not action.transition_state == "submitted":
            return
        receiver = action.request.receiver.resolve()
        if not isinstance(receiver, AutoApprover) or not receiver.value == "true":
            return

        action_obj = RequestActions.get_action(action.request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow)


# ----
class OARepoGenericActionMixin:
    # todo alternatively this can be abstract methods or mixins instead of components
    # podle me je to delat takhle prehlednejsi a snadneji spravovatelny nez mixiny nebo dekoratory, nemusi se
    # jmenovat komponenty kvuli konceptualni odlisnosti od invenia
    components = []
    user_execute = None
    invenio_execute = None

    def execute(self, identity, uow, *args, **kwargs):

        for c in self.components:
            c.before(self, identity, uow, *args, **kwargs)
        if self.user_execute:  # user defined action
            self.user_execute(identity, uow, *args, **kwargs)
        self.invenio_execute(identity, uow, *args, **kwargs)
        # super().execute(identity, uow, *args, **kwargs)  #todo invenio parent; this won't work in case of subclasses - specifically call the invenio part?
        for c in self.components:
            c.after(self, identity, uow, *args, **kwargs)
        # todo except Exception as e: # to eg. rollback changes from components
        #   for c in self.components:
        #       c.on_exception(self, identity, e, uow, *args, **kwargs)
        #    raise e


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    transition_state = "submitted"
    invenio_execute = actions.SubmitAction.execute
    components = [
        AutoAcceptComponent(),
        TopicStateChangeFromWorkflowComponent(),
        RequestIdentityComponent(),
    ]


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    transition_state = "rejected" # could be replaced by status_to if we keep them same (it's not in documentation)
    invenio_execute = actions.DeclineAction.execute
    components = [TopicStateChangeFromWorkflowComponent(), RequestIdentityComponent()]


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    transition_state = "approved"
    invenio_execute = actions.AcceptAction.execute
    components = [TopicStateChangeFromWorkflowComponent(), RequestIdentityComponent()]


# ----


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
