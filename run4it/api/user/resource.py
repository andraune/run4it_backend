"""API Resources for handling registration, login, logout etc."""
from flask_restful import Resource
from flask_apispec import use_kwargs, marshal_with
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from run4it.app.database import db
from .model import User
from .schema import user_schema


class Register(Resource):

    @use_kwargs(user_schema)
    @marshal_with(user_schema)
    def post(self, username, email, password, **kwargs):

        if User.find_by_username(username):
            return { "message": "User already exists(1)." }, 409

        if User.find_by_email(email):
            return { "message": "User already exists(2)." }, 409

        new_user = User(username, email, password, **kwargs)
        try:
            new_user.save()
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
        except:
            db.session.rollback()
            return { "message": "Unable to create user." }, 500

        return new_user, 201
