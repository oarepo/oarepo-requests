import marshmallow as ma
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.links import Link, LinksTemplate
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields

from oarepo_requests.utils import get_matching_service_for_record

def is_record(record, ctx):
    """Shortcut for links to determine if record is a record."""
    if not hasattr(record, "is_draft"):
        return True
    return not record.is_draft

def get_links_schema():
    # TODO possibly specify more
    return ma.fields.Dict(keys=ma.fields.String())


class RequestTypeSchema(ma.Schema):
    type_id = ma.fields.String()
    links = get_links_schema()
    # links = Links()

    @ma.post_dump
    def create_link(self, data, **kwargs):
        if "links" in data:
            return data
        if "record" not in self.context:
            raise ma.ValidationError(
                "record not in context for request types serialization"
            )
        type_id = data["type_id"]
        type = current_request_type_registry.lookup(type_id, quiet=True)
        record = self.context["record"]
        service = get_matching_service_for_record(record)
        link = ConditionalLink(
            cond=is_record,
            if_=Link(f"{{+api}}{service.config.url_prefix}{{id}}/requests/{type_id}"),
            else_=Link(
                f"{{+api}}{service.config.url_prefix}{{id}}/draft/requests/{type_id}"
            ),
        )
        template = LinksTemplate({"create": link}, context={"id": record["id"]})
        data["links"] = {"actions": template.expand(self.context["identity"], record)}
        return data


class NoneReceiverGenericRequestSchema(GenericRequestSchema):
    receiver = fields.Dict(allow_none=True)


class RequestsSchemaMixin:
    requests = ma.fields.List(
        ma.fields.Nested(NoneReceiverGenericRequestSchema)
    )  # TODO consider what happens due to different request types having their own schema; should the projection be universal here?
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
