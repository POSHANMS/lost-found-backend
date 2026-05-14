from marshmallow import Schema, fields, validate, validates, ValidationError

class RegisterSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)    # name must be 2-100 chars
    )
    email = fields.Email(required=True)         # validates email format automatically
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6)         # minimum 6 character password
    )
    phone = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=15)    # phone number length
    )
    department = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)