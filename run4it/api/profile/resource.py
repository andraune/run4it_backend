import datetime as dt
from flask_restful import Resource, request
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from flask_jwt_extended import jwt_required, get_jwt_identity
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from run4it.api.user import User
from .model import ProfileWeightHistory
from .schema import profile_schema, weight_schema, weights_schema
from sqlalchemy import and_

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
	@use_kwargs(weight_schema, locations={"query"}, error_status_code = 422)
	@marshal_with(weights_schema)
	def get(self, username, start_at=None, end_at=None):
		auth_username = get_jwt_identity()

		if auth_username != username:
			report_error_and_abort(422, "profile", "Profile not found")

		user = User.find_by_username(auth_username)

		if user.profile is None: # should not be possible to have a user without a profile
		   report_error_and_abort(422, "profile", "Profile not found")

		weight_list = []
		if start_at is not None and end_at is not None:
			start_date = dt.datetime(start_at.year, start_at.month, start_at.day, 0, 0, 0)
			end_date = dt.datetime(end_at.year, end_at.month, end_at.day, 23, 59, 59, 999999)
			weight_list = user.profile.weights.filter(and_(ProfileWeightHistory.created_at > start_date, ProfileWeightHistory.created_at < end_date)).order_by(ProfileWeightHistory.created_at.desc()).all()
		elif start_at is not None:
			start_date = dt.datetime(start_at.year, start_at.month, start_at.day, 0, 0, 0)
			weight_list = user.profile.weights.filter(ProfileWeightHistory.created_at > start_date).order_by(ProfileWeightHistory.created_at.desc()).all()
		elif end_at is not None:
			end_date = dt.datetime(end_at.year, end_at.month, end_at.day, 0, 0, 0)
			weight_list = user.profile.weights.filter(ProfileWeightHistory.created_at < end_date).order_by(ProfileWeightHistory.created_at.desc()).all()
		else:
			weight_list = user.profile.weights.order_by(ProfileWeightHistory.created_at.desc()).all()

		return weight_list
