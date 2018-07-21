"""The app module, containing the app factory function."""
from flask import Flask


def create_app(config_object, app_name):
    app = Flask(app_name)

    return app
