from marshmallow import Schema, validate, fields


class GoalSchema(Schema):
	filter = fields.Str(load_only=True)
	id = fields.Int(dump_only=True, required=True)
	startAt = fields.DateTime(attribute='start_at', dump_only=True, required=True)
	endAt = fields.DateTime(attribute='end_at', dump_only=True, required=True)
	duration = fields.Int(dump_only=True, required=True)
	startValue = fields.Float(attribute='start_value', dump_only=True, required=True)
	targetValue = fields.Float(attribute='target_value', dump_only=True, required=True)
	currentValue = fields.Float(attribute='current_value', dump_only=True, required=True)
	category= fields.Str(attribute='category_name', dump_only=True, required=True)

	class Meta:
		strict = True

goal_schema = GoalSchema()
goals_schema = GoalSchema(many=True)
