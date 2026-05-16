from marshmallow import Schema, fields, validate

class ClaimSchema(Schema):
    # answer to verification question — required
    answer = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    # optional message to owner
    message = fields.Str(
        load_default="",
        validate=validate.Length(max=500)
    )

class ClaimResponseSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["approved", "rejected"])
    )