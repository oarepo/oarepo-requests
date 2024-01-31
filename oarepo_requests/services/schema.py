import marshmallow as ma
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields
from marshmallow_utils.fields import Links


class RequestTypeSchema(ma.Schema):
    type = ma.fields.String()
    links = Links()


class NoneReceiverGenericRequestSchema(GenericRequestSchema):
    receiver = fields.Dict(allow_none=True)


class RequestsSchemaMixin:
    requests = ma.fields.List(
        ma.fields.Nested(NoneReceiverGenericRequestSchema)
    )  # TODO consider what happens due to different request types having their own schema; should the projection be universal here?
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
