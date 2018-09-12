"""The api module, containing the API factory function."""
from flask import Blueprint, Flask
from flask_restful import Api, Resource
from run4it.api.user.resource import Register, Confirmation


API_VERSION = 1
API_VERSION_STR = 'v{0}'.format(API_VERSION)


class ApiVersion(Resource):
    def get(self):
        return { 'version': API_VERSION }


def create_api(app):
    api_blueprint_name = 'api_{0}'.format(API_VERSION_STR)
    api_blueprint_url_prefix = "/{0}".format(API_VERSION_STR)
    api_blueprint = Blueprint(api_blueprint_name, __name__)
    api = Api(api_blueprint, catch_all_404s=True)
    api.add_resource(ApiVersion, "/")

    # User resources
    api.add_resource(Register, "/user/register")
    api.add_resource(Confirmation, "/user/confirmation")

    app.register_blueprint(api_blueprint, url_prefix=api_blueprint_url_prefix)
    return api
