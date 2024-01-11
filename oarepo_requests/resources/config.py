from invenio_records_resources.resources.records.config import RecordResourceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin


class OARepoRequestsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """"""

    blueprint_name = "oarepo-requests"
    url_prefix = "/requests"
    routes = {
        "list": "/",
    }
