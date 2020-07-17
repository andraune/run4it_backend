import datetime as dt
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
	categoryName = fields.Str(attribute='category_name', dump_only=True, required=True)
	categoryUnit = fields.Str(attribute='category_unit', dump_only=True, required=True)

	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # note: sets timezone to UTC, should only be used on dump

class GoalUpdateSchema(Schema):
	id = fields.Int(dump_only=True, required=True) # dump_only because ID is part of Url
	startAt = fields.DateTime(required=True, attribute='start_at')
	duration = fields.Int(required=True, validate=[validate.Range(min=1)])
	startValue = fields.Float(required=True, attribute='start_value')
	targetValue = fields.Float(required=True, attribute='target_value')
	categoryID = fields.Int(required=True, validate=[validate.Range(min=1)], attribute='category_id')

	class Meta:
		strict = True

class GoalCategorySchema(Schema):
	id = fields.Int(dump_only=True, required=True)
	name = fields.Str(dump_only=True, required=True)
	unit = fields.Str(dump_only=True, required=True)
	workoutCategoryName = fields.Str(dump_only=True, required=True, attribute="workout_category_name")

	class Meta:
		strict = True


goal_schema = GoalSchema()
goals_schema = GoalSchema(many=True)
goal_update_schema = GoalUpdateSchema()
goal_categories_schema = GoalCategorySchema(many=True)
