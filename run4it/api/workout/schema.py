from marshmallow import Schema, validate, fields
		

class WorkoutExtendedTrackDataPoint(Schema):
	latitude = fields.Float(dump_only=True, required=True)
	longitude = fields.Float(dump_only=True, required=True)
	elevation = fields.Integer(dump_only=True, required=True)
	duration = fields.Float(dump_only=True, required=True)
	distance = fields.Float(dump_only=True, required=True)
	speed = fields.Float(attribute='average_speed', dump_only=True, required=True)
	pace = fields.Str(attribute='average_pace', dump_only=True, required=True)
	heartBpm = fields.Int(attribute='heart_bpm', dump_only=True, required=True)

class WorkoutSchema(Schema):
	limit = fields.Int(load_only=True, validate=[validate.Range(min=1, max=999)])
	offset = fields.Int(load_only=True, validate=[validate.Range(min=0)])
	goalID = fields.Int(attribute='goal_id', load_only=True, validate=[validate.Range(min=0)])
	id = fields.Int(dump_only=True, required=True)
	name = fields.Str(dump_only=True, required=True)
	startAt = fields.DateTime(attribute='start_at', dump_only=True, required=True)
	distance = fields.Int(dump_only=True, required=True)
	duration = fields.Int(dump_only=True, required=True)
	climb = fields.Int(dump_only=True, required=True)
	edited = fields.Bool(dump_only=True, required=True)
	resourceFile = fields.Str(attribute='resource_file', dump_only=True, required=True)
	categoryName = fields.Str(attribute='category_name', dump_only=True, required=True)
	averageSpeed = fields.Float(attribute='average_speed', dump_only=True, required=True)
	averagePace = fields.Str(attribute='average_pace', dump_only=True, required=True)
	trackData = fields.List(fields.Nested(WorkoutExtendedTrackDataPoint), attribute='extended_track_data', dump_only=True, required=False)
	trackSplits = fields.List(fields.Nested(WorkoutExtendedTrackDataPoint), attribute='extended_split_data', dump_only=True, required=False)
	trackSummary = fields.Nested(WorkoutExtendedTrackDataPoint, attribute='extended_summary', dump_only=True, required=False)

	class Meta:
		strict = True
		datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00' # note: sets timezone to UTC, should only be used on dump

class WorkoutUpdateSchema(Schema):
	name = fields.Str(required=True, validate=[validate.Length(min=0, max=128)])
	startAt = fields.DateTime(attribute='start_at', required=True)
	distance = fields.Int(required=True, validate=[validate.Range(min=0)])
	duration = fields.Int(required=True, validate=[validate.Range(min=0)])
	categoryID = fields.Int(attribute='category_id', required=True, validate=[validate.Range(min=1)])
	climb = fields.Int(validate=[validate.Range(min=0)])
	edited = fields.Bool()

	class Meta:
		strict = True

class WorkoutCategorySchema(Schema):
	id = fields.Int(required=True, dump_only=True)
	name = fields.Str(required=True, dump_only=True)
	supports_gps_data = fields.Bool(required=True, dump_only=True)

	class Meta:
		strict = True

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_update_schema = WorkoutUpdateSchema()
workout_categories_schema = WorkoutCategorySchema(many=True)
