from invenio_requests.customizations import actions
from invenio_requests.customizations.actions import RequestActions
from invenio_requests.errors import CannotExecuteActionError


class AutoAcceptSubmitAction(actions.SubmitAction):
    log_event = True

    def execute(self, identity, uow):
        super().execute(identity, uow)
        action_obj = RequestActions.get_action(self.request, "accept")
        if not action_obj.can_execute():
            raise CannotExecuteActionError("accept")
        action_obj.execute(identity, uow)
