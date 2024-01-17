from marshmallow_utils.fields import Links
import marshmallow as ma



class RequestApiSchema(ma.Schema):
    type = ma.fields.String()
    links = Links()

class RequestsSchemaMixin:
    requests = ma.fields.List(ma.fields.Nested(RequestApiSchema))
    request_types = ma.fields.List(ma.fields.Nested(RequestApiSchema))