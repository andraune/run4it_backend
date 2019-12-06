"""The app module, containing the app factory function."""
from flask import Flask
from .commands import clean, init_test_data, tests
from .extensions import jwt, db, migrate, mail
from run4it.api.user import User, UserConfirmation
from run4it.api.profile import Profile, ProfileWeightHistory
from run4it.api.token import TokenRegistry
from run4it.api.discipline import DisciplineModel


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

def register_commands(app):
    app.cli.add_command(clean)
    app.cli.add_command(init_test_data)
    app.cli.add_command(tests)


def register_shell_context(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': User,
            'UserConfirmation': UserConfirmation,
            'Profile': Profile,
			'ProfileWeightHistory': ProfileWeightHistory,
            'TokenRegistry': TokenRegistry,
			'Discipline': DisciplineModel
        }

    app.shell_context_processor(shell_context)
