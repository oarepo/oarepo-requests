from invenio_requests.services.requests.config import RequestsServiceConfig

from invenio_requests.services.requests.links import RequestLink
from thesis.records.api import ThesisDraft
from thesis.services.records.service import ThesisService
from thesis.proxies import current_service
from invenio_records_resources.services.base.config import ServiceConfig


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """"""
    topic_record_cls = ThesisDraft
    #TODO in model builder project these into resource prefix
    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
    }
    topic_service = current_service

    topic_type_id = "thesis"
    topic_draft_type_id = "thesis_draft"

class RecordRequestsServiceConfig(ServiceConfig):
    """"""

class DraftRecordRequestsServiceConfig(RecordRequestsServiceConfig):
    """"""