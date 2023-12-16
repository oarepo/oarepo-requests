import copy

from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service, current_request_type_registry
from invenio_requests.customizations import RequestActions


class AllowedRequestsComponent(UIResourceComponent):
    """Service component which sets all data in the record."""

    def _add_available_requests(self, identity, record, dict_to_save_result, kwargs):
        # todo discriminate requests from other stuff which can be on parent in the future
        # todo what to throw if parent doesn't exist

        if not record:
            return

        available_requests = {}
        kwargs[dict_to_save_result]["allowed_requests"] = available_requests

        parent_copy = copy.deepcopy(record.data["parent"])
        requests = {
            k: v
            for k, v in parent_copy.items()
            if isinstance(v, dict) and "receiver" in v
        }  # todo more sensible request identification

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
                    saved_request_data["actions"].append(action_name) # noqa we are sure that saved_request_data exists


    def before_ui_detail(self, identity, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "extra_context", kwargs)

    def before_ui_edit(self, identity, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "extra_context", kwargs)

    def form_config(self, identity, record=None, errors=None, **kwargs):
        self._add_available_requests(identity, record, "form_config", kwargs)
