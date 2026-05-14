from marshmallow import Schema, fields, validate

class ClaimSchema(Schema):
    message = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=500)       # must explain why it's theirs
    )

class ClaimResponseSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["approved", "rejected"])    # only these two values allowed  
    )