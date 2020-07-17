import datetime as dt
import pytz
from flask_restful import request, Resource
from flask_apispec import marshal_with
from flask_jwt_extended import jwt_required
from webargs.flaskparser import use_kwargs
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from run4it.api.profile.auth_helper import get_auth_profile_or_abort
from .model import Goal, GoalCategory
from .schema import goal_schema, goals_schema, goal_update_schema, goal_categories_schema


class ProfileGoalList(Resource):
	@jwt_required
	@use_kwargs(goal_schema, locations={"query"})
	@marshal_with(goals_schema)
	def get(self, username, filter='', **kwargs):
		profile = get_auth_profile_or_abort(username, "goal")
		goals = None

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


	@jwt_required
	@use_kwargs(goal_update_schema, error_status_code = 422)
	@marshal_with(goal_schema)
	def post(self, username, start_at, duration, start_value, target_value, category_id):
		profile = get_auth_profile_or_abort(username, "goal")
		category = GoalCategory.get_by_id(category_id)

		if category is None:
			report_error_and_abort(422, "goal", "Goal category not found")

		utc_start_at = start_at - start_at.utcoffset()
		utc_end_at = utc_start_at + dt.timedelta(days=duration)
		now = dt.datetime.utcnow().replace(tzinfo=pytz.UTC)

		if utc_end_at < now:
			report_error_and_abort(422, "goal", "Goal already expired")
		
		if start_value == target_value:
			report_error_and_abort(422, "goal", "Goal target value equals start value")

		try:
			new_goal = Goal(profile.id, category, utc_start_at, utc_end_at, start_value, target_value)
			new_goal.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "goal", "Unable to create goal.")

		return new_goal, 200, {'Location': '{}/{}'.format(request.path, new_goal.id)}


class ProfileGoal(Resource):
	@jwt_required
	@marshal_with(goal_schema)
	def get(self, username, goal_id):
		profile = get_auth_profile_or_abort(username, "goal")
		goal = profile.get_goal_by_id(goal_id)

		if goal is None:
			report_error_and_abort(404, "goal", "Goal not found.")
		
		return goal


	@jwt_required
	@use_kwargs(goal_update_schema, error_status_code = 422)
	@marshal_with(goal_schema)
	def put(self, username, goal_id, start_at, duration, start_value, target_value, category_id, **kwargs):
		profile = get_auth_profile_or_abort(username, "goal")
		goal = profile.get_goal_by_id(goal_id)

		if goal is None:
			report_error_and_abort(422, "goal", "Goal not found")

		if goal.end_at < dt.datetime.utcnow():
			report_error_and_abort(422, "goal", "Goal already expired")
		
		category = GoalCategory.get_by_id(category_id)

		if category is None:
			report_error_and_abort(422, "goal", "Goal category not found")

		if start_value == target_value:
			report_error_and_abort(422, "goal", "Goal target value equals start value")

		utc_start_at = start_at - start_at.utcoffset()

		goal.category = category
		goal.start_at = utc_start_at
		goal.end_at = utc_start_at + dt.timedelta(days=duration)
		goal.start_value = start_value
		goal.target_value = target_value

		try:
			goal.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "goal", "Unable to update goal")

		return goal, 200


class GoalCategoryList(Resource):
	@marshal_with(goal_categories_schema)
	def get(self):			
		return GoalCategory.query.order_by(GoalCategory.name.asc()).all()
