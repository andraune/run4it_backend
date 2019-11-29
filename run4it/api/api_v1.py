"""The api module, containing the API factory function."""
from flask import Blueprint, Flask, current_app
from flask_restful import Api, Resource
from run4it.api.user.resource import (Register, Confirmation, Login, LoginRefresh,
                                        Logout, LogoutRefresh)

from run4it.api.token.resource import TokenList
from run4it.api.profile.resource import Profile


API_VERSION = 1
API_VERSION_STR = 'v{0}'.format(API_VERSION)


class ApiVersion(Resource):
    def get(self):
        return { 'version': API_VERSION, 'env': current_app.config['ENV'], 'todo': 'Logout, LogoutRefresh, WeightTable, TestTokenResource (support no data found)' }


def create_api(app):
    api_blueprint_name = 'api_{0}'.format(API_VERSION_STR)
    api_blueprint_url_prefix = "/{0}".format(API_VERSION_STR)
    api_blueprint = Blueprint(api_blueprint_name, __name__)
    api = Api(api_blueprint, catch_all_404s=True)
    api.add_resource(ApiVersion, "/")

    # User resources
    api.add_resource(Register, "/users")
    api.add_resource(Confirmation, "/users/confirmation")
    api.add_resource(Login, "/users/login")
    api.add_resource(LoginRefresh, "/users/loginRefresh")
    api.add_resource(Logout, "/users/logout")
    api.add_resource(LogoutRefresh, "/users/logoutRefresh")
    
    # Token resources (for user to see/revoke tokens)
    api.add_resource(TokenList, "/tokens")

    # Profile resources
    api.add_resource(Profile, "/profiles/<string:username>")


    app.register_blueprint(api_blueprint, url_prefix=api_blueprint_url_prefix)
    return api
