import datetime as dt
from marshmallow import Schema, validate, fields


class ProfileSchema(Schema):
	height = fields.Integer(validate=[validate.Range(0, 280)])
	weight = fields.Float(validate=[validate.Range(0.0, 999.9)])
	birthDate = fields.Date(attribute='birth_date', validate=[validate.Range(dt.date(1900, 1, 1), dt.date.today())])
	createdAt = fields.DateTime(attribute='created_at', dump_only=True)
	updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
	username = fields.Str(dump_only=True, required=True)

	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # not: sets timezone to UTC, should only be used on dump

class WeightSchema(Schema):
	startAt = fields.Date(attribute='start_at', load_only=True)
	endAt = fields.Date(attribute='end_at', load_only=True)
	weight = fields.Float(validate=[validate.Range(0.0, 999.9)])
	createdAt = fields.DateTime(attribute='created_at', dump_only=True)

	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # not: sets timezone to UTC, should only be used on dump


profile_schema = ProfileSchema()
weight_schema = WeightSchema()
weights_schema = WeightSchema(many=True)
