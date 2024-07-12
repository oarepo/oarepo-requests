import marshmallow as ma
from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services.base.links import Link, LinksTemplate
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields
from oarepo_runtime.records import is_published_record

from oarepo_requests.utils import get_matching_service_for_record


def get_links_schema():
    return ma.fields.Dict(
        keys=ma.fields.String()
    )  # value is either string or dict of strings (for actions)


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
            cond=is_published_record,
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
    )
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
