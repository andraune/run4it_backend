"""The app module, containing the app factory function."""
from flask import Flask
from . import commands
from .extensions import jwt, db, migrate, mail
from run4it.api.user.model import User, UserConfirmation, TokenRegistry


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
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.initdata)
    app.cli.add_command(commands.tests)


def register_shell_context(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': User,
            'UserConfirmation': UserConfirmation,
            'TokenRegistry': TokenRegistry
        }

    app.shell_context_processor(shell_context)
