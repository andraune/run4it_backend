from os import path
import pytz
import datetime as dt
from flask import current_app
from flask_restful import request, Resource
from flask_apispec import marshal_with
from flask_jwt_extended import jwt_required
from webargs.flaskparser import use_kwargs
from werkzeug.utils import secure_filename
from run4it.api.templates import report_error_and_abort
from run4it.api.profile.auth_helper import get_auth_profile_or_abort
from run4it.app.database import db
from .model import Workout, WorkoutCategory, WorkoutDataPoint
from .schema import workout_schema, workouts_schema, workout_update_schema


def is_valid_gpx_filename(filename):
	if filename != "":
		allowed_extensions = current_app.config["ALLOWED_UPLOAD_EXTENSIONS"]
		return "." in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
	else:
		return False

def save_uploaded_file_or_abort(uploaded_file, profile_name):
	tmp_filename = secure_filename("{0}_{1}".format(profile_name, uploaded_file.filename))
	tmp_filepath = path.join(current_app.config["GPX_UPLOAD_DIR"], tmp_filename)

	try:
		uploaded_file.save(tmp_filepath)
	except:
		report_error_and_abort(422, "workout", "Workout file could not be read.")

	return tmp_filepath	


class ProfileWorkoutList(Resource):
	@jwt_required
	@use_kwargs(workout_schema, locations={"query"})
	@marshal_with(workouts_schema)
	def get(self, username, limit=10, offset=0):
		profile = get_auth_profile_or_abort(username, "workout")
		return profile.get_workouts(limit, offset)
	
	@jwt_required
	@use_kwargs(workout_update_schema, error_status_code = 422)
	@marshal_with(workout_schema)	
	def post(self, username, name, start_at, distance, duration, category_id, climb=0, edited=False):
		profile = get_auth_profile_or_abort(username, "workout")
		category = WorkoutCategory.get_by_id(category_id)

		if category is None:
			report_error_and_abort(422, "workout", "Workout category not found")

		if name is None or name == "":
			name = category.name

		utc_start_at = start_at - start_at.utcoffset()
		now = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)

		if utc_start_at > now:
			report_error_and_abort(422, "workout", "Workout start time is in the future")

		try:
			new_workout = Workout(profile.id, category, name, utc_start_at, distance, duration, climb, None, edited)
			new_workout.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "workout", "Unable to create workout.")

		return new_workout, 200, {'Location': '{}/{}'.format(request.path, new_workout.id)}


class ProfileWorkout(Resource):
	@jwt_required
	@marshal_with(workout_schema)
	def get(self, username, workout_id):
		profile = get_auth_profile_or_abort(username, "workout")
		workout = profile.get_workout_by_id(workout_id)

		if workout is None:
			report_error_and_abort(404, "workout", "Workout not found.")

		workout.register_extended_data()
		return workout

	@jwt_required
	@use_kwargs(workout_update_schema, error_status_code = 422)
	@marshal_with(workout_schema)
	def put(self, username, workout_id, name, start_at, distance, duration, category_id, climb=None, edited=None):
		profile = get_auth_profile_or_abort(username, "workout")
		workout = profile.get_workout_by_id(workout_id)

		if workout is None:
			report_error_and_abort(422, "workout", "Workout not found")
	
		category = WorkoutCategory.get_by_id(category_id)

		if category is None:
			report_error_and_abort(422, "workout", "Workout category not found")

		if name is None or name == "":
			name = category.name	

		utc_start_at = start_at - start_at.utcoffset()
		now = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)

		if utc_start_at > now:
			report_error_and_abort(422, "workout", "Workout start time is in the future")
		
		workout.category = category
		workout.name = name
		workout.start_at = utc_start_at
		workout.distance = distance
		workout.duration = duration

		if climb is not None:
			workout.climb = climb
		
		if edited is not None:
			workout.edited = edited

		try:
			workout.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "workout", "Unable to update workout")

		return workout, 200

class ProfileWorkoutGpx(Resource):
	@jwt_required
	@marshal_with(workout_schema)
	def post(self, username):
		profile = get_auth_profile_or_abort(username, "workout")

		if request.files is None or len(request.files) != 1 or request.files["gpxfile"] is None:
			report_error_and_abort(422, "workout", "Workout file not provided.")
		
		uploaded_file = request.files["gpxfile"]

		if not is_valid_gpx_filename(uploaded_file.filename):
			report_error_and_abort(422, "workout", "Workout filename invalid.")

		tmp_filepath = save_uploaded_file_or_abort(uploaded_file, profile.username)

		try:
			category = WorkoutCategory.get_by_id(1)
			new_workout = Workout(profile.id, category, "Uploaded workout", dt.datetime.utcnow(), 1234, 181, 1, tmp_filepath, False)
			new_workout.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "workout", "Unable to create workout from file.")

		return new_workout, 200, {'Location': '{}/{}'.format(request.path, new_workout.id)}
