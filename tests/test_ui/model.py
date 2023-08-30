
from oarepo_ui.resources import (
    BabelComponent,
    RecordsUIResource,
    RecordsUIResourceConfig,
)
from oarepo_ui.resources.components import PermissionsComponent
from thesis.resources.records.ui import ThesisUIJSONSerializer

from oarepo_requests.components import AllowedRequestsComponent

"""
class ModelRecordIdProvider(RecordIdProviderV2):
    pid_type = "rec"


class ModelRecord(Record):
    index = IndexField("test_record")
    model_cls = RecordMetadata
    pid = PIDField(
        provider=ModelRecordIdProvider, context_cls=PIDFieldContext, create=True
    )


class ModelPermissionPolicy(RecordPermissionPolicy):
    can_create = [AnyUser(), SystemProcess()]
    can_search = [AnyUser(), SystemProcess()]
    can_read = [AnyUser(), SystemProcess()]


class ModelSchema(ma.Schema):
    title = ma.fields.String()

    class Meta:
        unknown = ma.INCLUDE


class ModelServiceConfig(RecordServiceConfig):
    record_cls = ModelRecord
    permission_policy_cls = ModelPermissionPolicy
    schema = ModelSchema

    url_prefix = "/simple-model"

    @property
    def links_item(self):
        return {
            "self": RecordLink("{+api}%s/{id}" % self.url_prefix),
            "ui": RecordLink("{+ui}%s/{id}" % self.url_prefix),
        }


class ModelService(RecordService):
    pass


class ModelUISerializer(MarshmallowSerializer):

    def __init__(self):

        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=ModelSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
"""


class ModelUIResourceConfig(RecordsUIResourceConfig):
    api_service = (
        "thesis"  # must be something included in oarepo, as oarepo is used in tests
    )

    blueprint_name = "thesis"
    url_prefix = "/thesis/"
    ui_serializer_class = ThesisUIJSONSerializer
    templates = {
        **RecordsUIResourceConfig.templates,
        "detail": {"layout": "test_detail.html", "blocks": {}},
        "search": {
            "layout": "test_detail.html",
        },
    }

    components = [BabelComponent, PermissionsComponent, AllowedRequestsComponent]


class ModelUIResource(RecordsUIResource):
    pass
