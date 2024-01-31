from invenio_records_resources.services.base.config import ServiceConfig
from invenio_requests.services.requests.config import RequestsServiceConfig
from invenio_requests.services.requests.links import RequestLink


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
    }


class RecordRequestsServiceConfig(ServiceConfig):
    """"""


class DraftRecordRequestsServiceConfig(RecordRequestsServiceConfig):
    """"""
