import marshmallow as ma
from marshmallow_utils.fields import Links

from oarepo_requests.schemas.marshmallow import NoneReceiverGenericRequestSchema


class RequestTypeSchema(ma.Schema):
    type = ma.fields.String()
    links = Links()


class RequestsSchemaMixin:
    requests = ma.fields.List(
        ma.fields.Nested(NoneReceiverGenericRequestSchema)
    )  # TODO consider what happens due to different request types having their own schema; should the projection be universal here?
    request_types = ma.fields.List(ma.fields.Nested(RequestTypeSchema))
