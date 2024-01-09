from invenio_requests.customizations import RequestType
from invenio_requests.proxies import current_requests_service
from oarepo_requests.actions.publish_draft import PublishDraftAcceptAction
from .generic import OARepoRequestType
from oarepo_requests.utils import open_request_exists, resolve_reference_dict
from invenio_records_resources.services.errors import PermissionDeniedError

class PublishDraftRequestType(OARepoRequestType):
    available_actions = {
        **RequestType.available_actions,
        "accept": PublishDraftAcceptAction,
    }

    receiver_can_be_none = True
