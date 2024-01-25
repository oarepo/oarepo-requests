from flask_resources import BaseListSchema
from flask_resources.serializers import JSONSerializer
from oarepo_runtime.resources import LocalizedUIJSONSerializer
from thesis.services.records.ui_schema import ThesisUISchema
from flask import g
from invenio_requests.proxies import current_request_type_registry
from ..services.ui_schema import get_request_ui_schema
from oarepo_runtime.i18n import get_locale


class OARepoRequestsUIJSONSerializer(LocalizedUIJSONSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=ThesisUISchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui", "identity": g.identity},
        )

    def dump_obj(self, obj):
        if hasattr(obj, "type"):
            type_ = obj.type
            if isinstance(type_, str):
                type_ = current_request_type_registry.lookup(obj.type, quiet=True)
            schema_cls = get_request_ui_schema(type_._create_marshmallow_schema())
        elif isinstance(obj, dict):
            type_ = current_request_type_registry.lookup(obj["type"], quiet=True)
            schema_cls = get_request_ui_schema(type_._create_marshmallow_schema())
        else:
            schema_cls = self.object_schema_cls
        return schema_cls(
            context={**self.schema_context, "locale": get_locale()}
        ).dump(obj)
