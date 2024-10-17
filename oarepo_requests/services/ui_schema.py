
import marshmallow as ma
from invenio_pidstore.errors import PIDDeletedError
from invenio_requests.proxies import current_request_type_registry, current_requests
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_requests.services.schemas import (
    CommentEventType,
    EventTypeMarshmallowField,
)
from marshmallow import validate
from oarepo_runtime.i18n import lazy_gettext as _
from oarepo_runtime.services.schema.marshmallow import BaseRecordSchema
from oarepo_runtime.services.schema.ui import LocalizedDateTime

from oarepo_requests.resolvers.ui import resolve
from oarepo_requests.services.schema import (
    NoneReceiverGenericRequestSchema,
    RequestTypeSchema,
    get_links_schema,
)


class UIReferenceSchema(ma.Schema):
    reference = ma.fields.Dict(validate=validate.Length(equal=1))
    # reference = ma.fields.Dict(ReferenceString)
    type = ma.fields.String()
    label = ma.fields.String()
    links = get_links_schema()

    @ma.pre_dump
    def create_reference(self, data, **kwargs):
        if data:
            return dict(reference=data)

    @ma.post_dump
    def dereference(self, data, **kwargs):
        if "resolved" not in self.context:
            try:
                return resolve(self.context["identity"], data["reference"])
            except PIDDeletedError:
                return {**data, "status": "removed"}
        resolved_cache = self.context["resolved"]
        return resolved_cache.dereference(data["reference"])


class UIRequestSchemaMixin:
    created = LocalizedDateTime(dump_only=True)
    updated = LocalizedDateTime(dump_only=True)

    name = ma.fields.String()
    description = ma.fields.String()

    stateful_name = ma.fields.String(dump_only=True)
    stateful_description = ma.fields.String(dump_only=True)

    created_by = ma.fields.Nested(UIReferenceSchema)
    receiver = ma.fields.Nested(UIReferenceSchema)
    topic = ma.fields.Nested(UIReferenceSchema)

    links = get_links_schema()

    payload = ma.fields.Raw()

    status_code = ma.fields.String()

    @ma.pre_dump
    def add_type_details(self, data, **kwargs):
        type = data["type"]
        type_obj = current_request_type_registry.lookup(type, quiet=True)
        if hasattr(type_obj, "description"):
            data["description"] = type_obj.description
        if hasattr(type_obj, "name"):
            data["name"] = type_obj.name

        stateful_name, stateful_description = self._get_stateful_labels(type_obj, data)
        data["stateful_name"] = stateful_name or data["name"]
        data["stateful_description"] = stateful_description or data["description"]

        return data

    def _get_stateful_labels(self, type_obj, data):
        stateful_name = None
        stateful_description = None
        try:
            topic = ResolverRegistry.resolve_entity(data["topic"], False)
            if topic:
                if hasattr(type_obj, "stateful_name"):
                    stateful_name = type_obj.stateful_name(
                        identity=self.context["identity"],
                        topic=topic,
                        # not very nice, but we need to pass the request object to the stateful_name function
                        request=SimpleNamespace(**data),
                    )
                if hasattr(type_obj, "stateful_description"):
                    stateful_description = type_obj.stateful_description(
                        identity=self.context["identity"],
                        topic=topic,
                        # not very nice, but we need to pass the request object to the stateful_description function
                        request=SimpleNamespace(**data),
                    )
        except PIDDeletedError:
            pass

        return stateful_name, stateful_description

    @ma.pre_dump
    def process_status(self, data, **kwargs):
        data["status_code"] = data["status"]
        data["status"] = _(data["status"].capitalize())
        return data


class UIBaseRequestSchema(UIRequestSchemaMixin, NoneReceiverGenericRequestSchema):
    """"""


class UIRequestTypeSchema(RequestTypeSchema):
    name = ma.fields.String()
    description = ma.fields.String()
    fast_approve = ma.fields.Boolean()

    stateful_name = ma.fields.String(dump_only=True)
    stateful_description = ma.fields.String(dump_only=True)

    dangerous = ma.fields.Boolean(dump_only=True)
    editable = ma.fields.Boolean(dump_only=True)
    has_form = ma.fields.Boolean(dump_only=True)

    @ma.post_dump
    def add_type_details(self, data, **kwargs):
        type = data["type_id"]
        type_obj = current_request_type_registry.lookup(type, quiet=True)
        if hasattr(type_obj, "description"):
            data["description"] = type_obj.description
        if hasattr(type_obj, "name"):
            data["name"] = type_obj.name
        if hasattr(type_obj, "dangerous"):
            data["dangerous"] = type_obj.dangerous
        if hasattr(type_obj, "editable"):
            data["editable"] = type_obj.editable
        if hasattr(type_obj, "has_form"):
            data["has_form"] = type_obj.has_form

        if hasattr(type_obj, "stateful_name"):
            data["stateful_name"] = type_obj.stateful_name(
                identity=self.context["identity"], topic=self.context["topic"]
            )
        if hasattr(type_obj, "stateful_description"):
            data["stateful_description"] = type_obj.stateful_description(
                identity=self.context["identity"], topic=self.context["topic"]
            )
        return data


class UIRequestsSerializationMixin(ma.Schema):
    @ma.post_dump()
    def add_request_types(self, data, **kwargs):
        expanded = data.get("expanded", {})
        if not expanded:
            return data
        context = {**self.context, "topic": data}
        if "request_types" in expanded:
            expanded["request_types"] = UIRequestTypeSchema(context=context).dump(
                expanded["request_types"], many=True
            )
        if "requests" in expanded:
            expanded["requests"] = UIBaseRequestSchema(context=context).dump(
                expanded["requests"], many=True
            )
        return data


class UIBaseRequestEventSchema(BaseRecordSchema):
    created = LocalizedDateTime(dump_only=True)
    updated = LocalizedDateTime(dump_only=True)

    type = EventTypeMarshmallowField(dump_only=True)
    created_by = ma.fields.Nested(UIReferenceSchema)
    permissions = ma.fields.Method("get_permissions", dump_only=True)
    payload = ma.fields.Raw()

    def get_permissions(self, obj):
        """Return permissions to act on comments or empty dict."""
        type = self.get_attribute(obj, "type", None)
        is_comment = type == CommentEventType
        if is_comment:
            service = current_requests.request_events_service
            return {
                "can_update_comment": service.check_permission(
                    self.context["identity"], "update_comment", event=obj
                ),
                "can_delete_comment": service.check_permission(
                    self.context["identity"], "delete_comment", event=obj
                ),
            }
        else:
            return {}
