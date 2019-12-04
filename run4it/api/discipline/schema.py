from marshmallow import Schema, validate, fields


class DisciplineSchema(Schema):
	limit = fields.Int(load_only=True)
	offset = fields.Int(load_only=True)
	id = fields.Int(dump_only=True, required=True)
	name = fields.Str(dump_only=True, required=True)
	length = fields.Int(dump_only=True, required=True)
	username = fields.Str(dump_only=True, required=True)

	class Meta:
		strict = True

class DisciplineUpdateSchema(Schema):
	id = fields.Int(dump_only=True, required=True)
	name = fields.Str(required=True, validate=[validate.Length(min=2, max=16)], error_messages={'required': 'Name is required.'})
	length = fields.Int(required=True, validate=[validate.Length(min=1, max=999999)], error_messages={'required': 'Length is required.'})
	username = fields.Str(dump_only=True, required=True)

	class Meta:
		strict = True


discipline_schema = DisciplineSchema()
disciplines_schema = DisciplineSchema(many=True)
discipline_update_schema = DisciplineUpdateSchema()
