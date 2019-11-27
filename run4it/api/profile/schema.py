from marshmallow import Schema, validate, fields


class ProfileSchema(Schema):
    height = fields.Integer(validate=[validate.Range(0, 280)])
    birth_date = fields.Date()
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    username = fields.Str(required=True, dump_only=True)
    
    class Meta:
        strict = True   


profile_schema = ProfileSchema()
