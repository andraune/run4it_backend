from marshmallow import Schema, validate, fields

class BaseUserSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=4, max=16)], error_messages={'required': 'Username is required.'})

class UserSchema(BaseUserSchema):
    email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
    password = fields.Str(load_only=True, required=True, validate=[validate.Length(min=6, max=32)], error_messages={'required': 'Password is required.'})
    confirmed = fields.Bool(dump_only=True, required=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    
    class Meta:
        strict = True

class ConfirmationSchema(BaseUserSchema):
    confirmationCode = fields.Str(attribute='confirmation_code', load_only=True, required=True, validate=[validate.Length(min=1, max=128)], error_messages={'required': 'Confirmation code is required.'})
    
    class Meta:
        strict = True


user_schema = UserSchema()
confirmation_schema = ConfirmationSchema()
