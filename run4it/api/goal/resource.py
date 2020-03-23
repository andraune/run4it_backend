from flask_restful import Resource
from flask_apispec import marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_kwargs
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from run4it.api.user import User
from .model import Goal
from .schema import goal_schema, goals_schema

def _get_auth_profile(username):
	auth_username = get_jwt_identity()
	if auth_username != username:
		report_error_and_abort(422, "goal", "Profile not found")

	user = User.find_by_username(auth_username)
	if user.profile is None: # should not be possible to have a user without a profile
		report_error_and_abort(422, "goal", "Profile not found")

	return user.profile

class ProfileGoalList(Resource):
	@jwt_required
	@use_kwargs(goal_schema, locations={"query"})
	@marshal_with(goals_schema)
	def get(self, username, filter='', **kwargs):
		profile = _get_auth_profile(username)

		if filter == 'expired':
			goals = profile.get_expired_goals()
		elif filter == 'future':
			goals = profile.get_future_goals()
		elif filter == 'completed':
			goals = profile.get_completed_goals()
		elif filter == 'incompleted':
			goals = profile.get_incompleted_goals()
		else:
			goals = profile.get_active_goals()
		return goals
