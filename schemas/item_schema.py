from marshmallow import Schema, fields, validate

class ItemSchema(Schema):
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=150)
    )

    description = fields.Str(
        required=True,
        validate=validate.Length(min=10)            # at least 10 chars description
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf([
            "Electronics", "Documents", "Accessories",
            "Clothing", "Keys", "Bags", "Other"
        ])
    )
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["lost", "found"])      # only lost or found allowed
    )
    location = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200)
    )
    latitude = fields.Float(load_default=None)      # optional
    longitude = fields.Float(load_default=None)     # optional