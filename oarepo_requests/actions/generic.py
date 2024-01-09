from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import actions

from ..utils import get_matching_service

"""

not needed for now

def set_request_on_parent(request, uow):
    topic = request.topic.resolve()
    topic_service = get_matching_service(topic)
    if topic is not None:
        setattr(topic.parent, request.type.type_id, request)
        uow.register(
            RecordCommitOp(topic, indexer=topic_service.indexer, index_refresh=True)
        )

        # the database query for topic parent is needed only for this; i'm leaving it here for reference and explanation 
        #for ext in topic.parent._extensions:
        #    from invenio_records.systemfields.base import SystemFieldsExt
        #    if isinstance(ext, SystemFieldsExt):
        #        ext.declared_fields[request.type.type_id].pre_commit(topic.parent)


        uow.register(RecordCommitOp(topic.parent))


def unset_request_on_parent(request, uow):
    topic = request.topic.resolve()
    if topic is not None:
        setattr(topic.parent, request.type.type_id, None)
        uow.register(RecordCommitOp(topic.parent, index_refresh=True))


class CreateAction(actions.CreateAction):
    def execute(self, identity, uow):
        super().execute(identity, uow)
        set_request_on_parent(self.request, uow)


class SubmitAction(actions.SubmitAction):
    def execute(self, identity, uow):
        super().execute(identity, uow)
        set_request_on_parent(self.request, uow)


class CreateAndSubmitAction(actions.CreateAndSubmitAction):

    def execute(self, identity, uow):
        super().execute(identity, uow)
        set_request_on_parent(self.request, uow)


class AcceptAction(actions.AcceptAction):


    def execute(self, identity, uow):
        super().execute(identity, uow)
        unset_request_on_parent(self.request, uow)


class DeleteAction(actions.DeleteAction):


    def execute(self, identity, uow):
        super().execute(identity, uow)
        unset_request_on_parent(self.request, uow)


class CancelAction(actions.CancelAction):


    def execute(self, identity, uow):
        super().execute(identity, uow)
        unset_request_on_parent(self.request, uow)


class ExpireAction(actions.ExpireAction):


    def execute(self, identity, uow):
        super().execute(identity, uow)
        unset_request_on_parent(self.request, uow)


class DeclineAction(actions.DeclineAction):


    def execute(self, identity, uow):
        super().execute(identity, uow)
        unset_request_on_parent(self.request, uow)
"""
