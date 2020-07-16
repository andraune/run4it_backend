from marshmallow import Schema, validate, fields


class UserSchema(Schema):
	username = fields.Str(required=True, validate=[validate.Regexp('^[a-zA-Z]{1}[a-zA-Z0-9_]{3,15}$', 0, error='Username must be 4-16 characters: a-z, A-Z, 0-9 and underscore')], error_messages={'required': 'Username is required.'})
	email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
	password = fields.Str(load_only=True, required=True, validate=[validate.Length(min=6, max=32)], error_messages={'required': 'Password is required.'})
	confirmed = fields.Bool(dump_only=True, required=True)
	createdAt = fields.DateTime(attribute='created_at', dump_only=True)
	updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
	accessToken = fields.Str(attribute='access_token', dump_only=True)
	refreshToken = fields.Str(attribute='refresh_token', dump_only=True)
	
	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # not: sets timezone to UTC, should only be used on dump

class ConfirmationSchema(Schema):
	username = fields.Str(required=True, error_messages={'required': 'Username is required.'})
	confirmationCode = fields.Str(attribute='confirmation_code', load_only=True, required=True, validate=[validate.Length(min=1, max=128)], error_messages={'required': 'Confirmation code is required.'})
	
	class Meta:
		strict = True


class LoginSchema(Schema):
	email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
	password = fields.Str(load_only=True, required=True, error_messages={'required': 'Password is required.'})
	
	class Meta:
		strict = True    


user_schema = UserSchema()
confirmation_schema = ConfirmationSchema()
login_schema = LoginSchema()
