from marshmallow import Schema, validate, fields


class UserSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=4, max=16)], error_messages={'required': 'Username is required.'})
    email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
    password = fields.Str(load_only=True, required=True, validate=[validate.Length(min=6, max=32)], error_messages={'required': 'Password is required.'})
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at')

    class Meta:
        strict = True

user_schema = UserSchema()
