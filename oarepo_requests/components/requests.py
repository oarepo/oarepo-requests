import copy
import functools
from collections import defaultdict

from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import LogEventType, RequestActions
from invenio_requests.proxies import (
    current_events_service,
    current_request_type_registry,
    current_requests_service,
)

from invenio_communities.proxies import current_roles, current_communities
from invenio_communities.generators import CommunityRoles
"""
class RecordCommunitiesAction(CommunityRoles):

    def __init__(self, action):
        self._action = action

    def roles(self, **kwargs):
        return {r.name for r in current_roles.can(self._action)}
"""

class AllowedRequestsComponent(ServiceComponent):
    """Service component which sets all data in the record."""
    def _add_available_requests(self, identity, record, dict_to_save_result, **kwargs):

        # todo discriminate requests from other stuff which can be on parent in the future
        # todo what to throw if parent doesn't exist
        parent_copy = copy.deepcopy(record["parent"])
        requests = {k: v for k,v in parent_copy.items() if isinstance(v, dict) and 'receiver' in v} # todo more sensible request identification
        available_requests = {}

        for request_name, request_dict in requests.items():
            request = current_requests_service.record_cls.get_record(request_dict["id"])
            request_type = current_request_type_registry.lookup(request_dict["type"])
            for action_name, action in request_type.available_actions.items():
                try:
                    current_requests_service.require_permission(
                        identity, f"action_{action_name}", request=request
                    )
                except PermissionDeniedError:
                    continue
                action = RequestActions.get_action(request, action_name)
                if not action.can_execute():
                    continue
                if request_name not in available_requests:
                    saved_request_data = copy.deepcopy(request_dict)
                    saved_request_data["actions"] = [action_name]
                    available_requests[request_name] = saved_request_data
                else:
                    saved_request_data["actions"].append(action_name)

        dict_to_save_result = kwargs[dict_to_save_result]
        dict_to_save_result["allowed_requests"] = available_requests
    def before_ui_detail(self, identity, data=None, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "extra_context", **kwargs)
    def before_ui_edit(self, identity, data=None, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "extra_context", **kwargs)
    def form_config(self, identity, data=None, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "form_config", **kwargs)


class PublishDraftComponentPrivate(ServiceComponent):
    """Service component for request integration."""

    def __init__(self, publish_request_type, delete_request_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.publish_request_type = publish_request_type
        self.delete_request_type = delete_request_type

    def create(self, identity, data=None, record=None, **kwargs):
        """Create the review if requested."""
        # topic and request_type in kwargs
        if self.publish_request_type:
            type_ = current_request_type_registry.lookup(
                self.publish_request_type, quiet=True
            )
            request_item = current_requests_service.create(
                identity, {}, type_, receiver=None, topic=record, uow=self.uow
            )
            setattr(record.parent, self.publish_request_type, request_item._request)
            self.uow.register(RecordCommitOp(record.parent))

    def publish(self, identity, data=None, record=None, **kwargs):
        publish_request = getattr(record.parent, self.publish_request_type)

        if publish_request is not None:
            request = publish_request.get_object()
            request_status = "accepted"
            request.status = request_status
            setattr(record.parent, self.publish_request_type, None)
            event = LogEventType(
                payload={
                    "event": request_status,
                    "content": "record was published through direct call without request",
                }
            )
            _data = dict(payload=event.payload)
            current_events_service.create(
                identity, request.id, _data, event, uow=self.uow
            )

        if self.delete_request_type:
            type_ = current_request_type_registry.lookup(
                self.delete_request_type, quiet=True
            )
            request_item = current_requests_service.create(
                identity, {}, type_, receiver=None, topic=record, uow=self.uow
            )
            setattr(record.parent, self.delete_request_type, request_item._request)
            self.uow.register(RecordCommitOp(record.parent))


def PublishDraftComponent(publish_request_type, delete_request_type):
    return functools.partial(
        PublishDraftComponentPrivate, publish_request_type, delete_request_type
    )
