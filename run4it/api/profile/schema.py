import datetime as dt
from marshmallow import Schema, validate, fields


class ProfileSchema(Schema):
    height = fields.Integer(validate=[validate.Range(0, 280)])
    birth_date = fields.Date(validate=[validate.Range(dt.date(1900, 1, 1), dt.date.today())])
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    username = fields.Str(dump_only=True, required=True)

    class Meta:
        strict = True


profile_schema = ProfileSchema()
