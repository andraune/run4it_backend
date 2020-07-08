import datetime as dt
from flask_restful import Resource, request
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from flask_jwt_extended import jwt_required, get_jwt_identity
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from run4it.api.user import User
from .model import ProfileWeightHistory
from .schema import profile_schema, weights_schema


class Profile(Resource):
	@jwt_required
	@marshal_with(profile_schema)
	def get(self, username, **kwargs):	
		auth_username = get_jwt_identity()

		if auth_username != username:
			report_error_and_abort(422, "profile", "Profile not found")

		user = User.find_by_username(auth_username)

		if user.profile is None: # should not be possible to have a user without a profile
		   report_error_and_abort(422, "profile", "Profile not found") 
		
		# load profile from db
		return user.profile, 200

	@jwt_required
	@use_kwargs(profile_schema, error_status_code = 422)
	@marshal_with(profile_schema)
	def put(self, username, height=None, weight=None, birth_date=None, **kwargs):
		auth_username = get_jwt_identity()

		if auth_username != username:
			report_error_and_abort(422, "profile", "Profile not found")

		user = User.find_by_username(auth_username)	

		if user.profile is None: # should not be possible to have a user without a profile
		   report_error_and_abort(422, "profile", "Profile not found")

		was_updated = False
		
		if (height is not None):
			user.profile.set_height(height)
			was_updated = True

		if (weight is not None):
			user.profile.set_weight(weight)
			was_updated = True

		if birth_date is not None:
			user.profile.birth_date = birth_date
			was_updated = True

		if was_updated:
			try:
				user.profile.updated_at = dt.datetime.utcnow()
				user.save()
			except:
				db.session.rollback()
				report_error_and_abort(500, "profile", "Unable to update profile")

		return user.profile, 200


class ProfileWeight(Resource):
	@jwt_required
	@marshal_with(weights_schema)
	def get(self, username, **kwargs):
		auth_username = get_jwt_identity()

		if auth_username != username:
			report_error_and_abort(422, "profile", "Profile not found")

		user = User.find_by_username(auth_username)

		if user.profile is None: # should not be possible to have a user without a profile
		   report_error_and_abort(422, "profile", "Profile not found")

		weight_list = user.profile.weights.all()
		return weight_list
