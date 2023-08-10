from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields

class NoneReceiverGenericRequestSchema(GenericRequestSchema):
    receiver = fields.Dict(allow_none=True)