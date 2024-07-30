from functools import cached_property

from invenio_requests.customizations import actions

from oarepo_requests.proxies import current_oarepo_requests


class OARepoGenericActionMixin:
    def apply(self, identity, uow, *args, **kwargs):
        pass

    @cached_property
    def components(self):
        return [
            component_cls()
            for component_cls in current_oarepo_requests.action_components(self)
        ]

    def execute(self, identity, uow, *args, **kwargs):
        for c in self.components:
            c.before(self, identity, uow, *args, **kwargs)
        self.apply(identity, uow, *args, **kwargs)
        super().execute(identity, uow, *args, **kwargs)
        for c in self.components:
            c.after(self, identity, uow, *args, **kwargs)
        # todo except Exception as e: # to eg. rollback changes from components
        #   for c in self.components:
        #       c.on_exception(self, identity, e, uow, *args, **kwargs)
        #    raise e


class OARepoSubmitAction(OARepoGenericActionMixin, actions.SubmitAction):
    transition_state = "submitted"


class OARepoDeclineAction(OARepoGenericActionMixin, actions.DeclineAction):
    transition_state = "rejected"  # could be replaced by status_to if we keep them same (it's not in documentation)


class OARepoAcceptAction(OARepoGenericActionMixin, actions.AcceptAction):
    transition_state = "approved"
