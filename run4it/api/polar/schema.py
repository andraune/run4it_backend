import datetime as dt
from marshmallow import Schema, validate, fields


class PolarAuthCallbackSchema(Schema):
	state = fields.Str(required=False)
	code = fields.Str(required=False)
	error = fields.Str(required=False)

	class Meta:
		strict = True

class PolarWebhookSchema(Schema):
	event = fields.Str(required=False)
	timestamp = fields.DateTime(required=False)
	user_id = fields.Int(required=False)
	entity_id = fields.Str(required=False)
	url = fields.Str(required=False)

	class Meta:
		strict = True


class PolarUserSchema(Schema):
	profileID = fields.Int(attribute='profile_id', dump_only=True, required=True)
	memberID = fields.Str(attribute='member_id', dump_only=True, required=True)
	polarUserID = fields.Int(attribute='polar_user_id', dump_only=True, required=True)
	accessTokenExpiresAt = fields.DateTime(attribute='access_token_expires', dump_only=True, required=True)
	updatedAt = fields.DateTime(attribute='updated_at', dump_only=True, required=True)
	authUrl = fields.Str(attribute='auth_url', dump_only=True, required=False)

	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # note: sets timezone to UTC, should only be used on dump


polar_callback_schema = PolarAuthCallbackSchema()
polar_webhook_schema = PolarWebhookSchema()
polar_user_schema = PolarUserSchema()
