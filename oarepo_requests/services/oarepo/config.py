from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
    }
