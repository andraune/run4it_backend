"""API Resources for handling registration, login, logout etc."""
from flask_restful import Resource, request
from flask_apispec import use_kwargs, marshal_with
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from run4it.app.database import db
from run4it.app.extensions import mail
from run4it.api.exceptions import report_error_and_abort
from .model import User, UserConfirmation
from .schema import user_schema, confirmation_schema


class Register(Resource):
    @use_kwargs(user_schema)
    @marshal_with(user_schema)
    def post(self, username, email, password, **kwargs):

        if User.find_by_username(username):
            report_error_and_abort(409, "register", "User already exists(1)")

        if User.find_by_email(email):
            report_error_and_abort(409, "register", "User already exists(2)")

        new_user = User(username, email, password, **kwargs)
        confirmation = UserConfirmation(username, None, **kwargs)

        try:
            confirmation.save()
            new_user.save()

            #TODO: Remove from here
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
        except:
            db.session.rollback()
            report_error_and_abort(500, "register", "Unable to create user")

        return new_user, 201, {'Location': request.path.replace('/register', '/{0}'.format(new_user.id), 1) }


class Confirmation(Resource):
    CONFIRMATION_CODE_EXPIRY_S = 3600

    @use_kwargs(confirmation_schema)
    @marshal_with(user_schema)
    def post(self, username, confirmation_code, **kwargs):

        user = User.find_by_username(username)

        if not user:
            report_error_and_abort(422, "confirmation", "Confirmation failed(1)")
        
        confirmation = UserConfirmation.find_by_username(username)
        
        if not confirmation:
            report_error_and_abort(422, "confirmation", "Confirmation failed(2)")

        if not confirmation.check_code(confirmation_code):
            report_error_and_abort(422, "confirmation", "Confirmation failed(3)")

        if not confirmation.check_expiration(self.CONFIRMATION_CODE_EXPIRY_S):
            report_error_and_abort(422, "confirmation", "Confirmation failed(4)")

        # If we reach here we have a valid user and confirmation code
        try:
            confirmation.delete()
            user.confirmed = True
            user.save()
        except:
            db.session.rollback()
            report_error_and_abort(500, "confirmation", "Unable to confirm user")

        return user, 200

