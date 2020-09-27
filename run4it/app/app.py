"""The app module, containing the app factory function."""
from flask import Flask
from .commands import clean, init_test_data, tests, script4it
from .extensions import jwt, db, migrate, mail, cors
from run4it.api.discipline import DisciplineModel
from run4it.api.goal import GoalModel, GoalCategoryModel
from run4it.api.profile import Profile, ProfileWeightHistory
from run4it.api.token import TokenRegistry
from run4it.api.user import User, UserConfirmation
from run4it.api.workout import WorkoutCategoryModel, WorkoutModel
from run4it.api.workout.gmaps import GeoCodeLookup
from run4it.api.polar import PolarUserModel, PolarWebhookExerciseModel
from run4it.api.scripts import ScriptModel


def create_app(config_object, app_name):
	app = Flask(app_name)
	app.url_map.strict_slashes = False
	app.config.from_object(config_object)

	register_extensions(app)
	register_commands(app)
	register_shell_context(app)

	return app

def register_extensions(app):
	"""Register Flask extensions"""
	jwt.init_app(app)
	db.init_app(app)
	migrate.init_app(app, db)
	mail.init_app(app)
	cors.init_app(app, origins=app.config.get('CORS_ORIGIN_WHITELIST', '*'))

def register_commands(app):
	"""Register shell commands"""
	app.cli.add_command(clean)
	app.cli.add_command(init_test_data)
	app.cli.add_command(tests)
	app.cli.add_command(script4it)


def register_shell_context(app):
	"""Register shell context objects."""
	def shell_context():
		"""Shell context objects."""
		return {
			'db': db,
			'Discipline': DisciplineModel,
			'Goal': GoalModel,
			'GoalCategory': GoalCategoryModel,
			'Profile': Profile,
			'ProfileWeightHistory': ProfileWeightHistory,
			'TokenRegistry': TokenRegistry,
			'User': User,
			'UserConfirmation': UserConfirmation,
			'Workout': WorkoutModel,
			'WorkoutCategory': WorkoutCategoryModel,
			'GeoCodeLookup': GeoCodeLookup,
            'PolarUser': PolarUserModel,
			'PolarWebhookExercise': PolarWebhookExerciseModel,
			'Script': ScriptModel
		}

	app.shell_context_processor(shell_context)
