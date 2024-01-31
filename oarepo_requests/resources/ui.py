from flask import g
from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from invenio_requests.proxies import current_request_type_registry
from oarepo_runtime.i18n import get_locale
from oarepo_runtime.resources import LocalizedUIJSONSerializer

from ..services.ui_schema import UIBaseRequestSchema, get_request_ui_schema


class OARepoRequestsUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIBaseRequestSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )
