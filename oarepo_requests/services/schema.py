import marshmallow as ma
from invenio_records_resources.services.base.links import Link, LinksTemplate
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields

from oarepo_requests.proxies import current_oarepo_requests_resource


def get_links_schema():
    # TODO possibly specify more
    return ma.fields.Dict(keys=ma.fields.String())


class RequestTypeSchema(ma.Schema):
    type_id = ma.fields.String()
    links = get_links_schema()
    # links = Links()

    @ma.post_dump
    def create_link(self, data, **kwargs):
        type_id = data["type_id"]
        type = current_request_type_registry.lookup(type_id, quiet=True)
        link = Link(f"{{+api}}{current_oarepo_requests_resource.config.url_prefix}")
        template = LinksTemplate({"create": link})
        data["links"] = {"actions": template.expand(self.context["identity"], type)}
        return data


class NoneReceiverGenericRequestSchema(GenericRequestSchema):
    receiver = fields.Dict(allow_none=True)


class RequestsSchemaMixin:
    requests = ma.fields.List(
        ma.fields.Nested(NoneReceiverGenericRequestSchema)
    )  # TODO consider what happens due to different request types having their own schema; should the projection be universal here?
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
