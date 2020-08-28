"""The api module, containing the API factory function."""
import logging
from flask import Blueprint, Flask, current_app
from flask_restful import Api, Resource
from run4it.api.user.resource import (UserResource, Register, Confirmation, Login, LoginFresh, LoginRefresh,
										Logout, LogoutRefresh)

from run4it.api.token.resource import Token, TokenList
from run4it.api.profile.resource import Profile, ProfileWeight
from run4it.api.discipline import DisciplineResource, DisciplineListResource
from run4it.api.goal import ProfileGoalListResource, ProfileGoalResource, GoalCategoryListResource
from run4it.api.polar import ProfilePolarResource, PolarWebhookExerciseResource, PolarAuthorizationCallbackResource
from run4it.api.workout import ProfileWorkoutListResource, ProfileWorkoutResource, ProfileWorkoutGpxResource, WorkoutCategoryListResource


API_VERSION = 1
API_VERSION_STR = 'v{0}'.format(API_VERSION)


class ApiVersion(Resource):
	def get(self):
		return { 'version': API_VERSION, 'env': current_app.config['ENV'] }


def create_api(app):
	api_blueprint_name = 'api_{0}'.format(API_VERSION_STR)
	api_blueprint_url_prefix = "/{0}".format(API_VERSION_STR)
	api_blueprint = Blueprint(api_blueprint_name, __name__)
	api = Api(api_blueprint, catch_all_404s=True)
	api.add_resource(ApiVersion, "/")

	# User resources
	api.add_resource(UserResource, "/user")
	api.add_resource(Register, "/users")
	api.add_resource(Confirmation, "/users/confirmation")
	api.add_resource(Login, "/users/login")
	api.add_resource(LoginFresh, "/users/loginFresh")
	api.add_resource(LoginRefresh, "/users/loginRefresh")
	api.add_resource(Logout, "/users/logout")
	api.add_resource(LogoutRefresh, "/users/logoutRefresh")
	
	# Token resources (for user to see/revoke tokens)
	api.add_resource(TokenList, "/tokens")
	api.add_resource(Token, "/tokens/<int:token_id>")

	# Profile resources
	api.add_resource(Profile, "/profiles/<string:username>")
	api.add_resource(ProfileWeight, "/profiles/<string:username>/weight")
	
	# Profile goal resources
	api.add_resource(ProfileGoalListResource, "/profiles/<string:username>/goals")
	api.add_resource(ProfileGoalResource, "/profiles/<string:username>/goals/<int:goal_id>")

	# Profile workout resources
	api.add_resource(ProfileWorkoutListResource, "/profiles/<string:username>/workouts")
	api.add_resource(ProfileWorkoutGpxResource, "/profiles/<string:username>/workouts/gpx/<int:category_id>")
	api.add_resource(ProfileWorkoutResource, "/profiles/<string:username>/workouts/<int:workout_id>")

	# Profile polar resources
	api.add_resource(ProfilePolarResource, "/profiles/<string:username>/polar") 

	# Polar resources
	api.add_resource(PolarAuthorizationCallbackResource, "/polar/authorization_callback", resource_class_kwargs={'logger': logging.getLogger('file')})
	api.add_resource(PolarWebhookExerciseResource, "/polar/webhook", resource_class_kwargs={'logger': logging.getLogger('file')})

	# Discipline resources
	api.add_resource(DisciplineListResource, "/disciplines")
	api.add_resource(DisciplineResource, "/disciplines/<int:disc_id>")

	# Goal category resources
	api.add_resource(GoalCategoryListResource, "/goal_categories")

	# Workout category resources
	api.add_resource(WorkoutCategoryListResource, "/workout_categories")

	app.register_blueprint(api_blueprint, url_prefix=api_blueprint_url_prefix)
	return api
