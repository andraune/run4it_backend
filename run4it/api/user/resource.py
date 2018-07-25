"""API Resources for handling registration, login, logout etc."""
from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from webargs import fields, validate
from webargs.flaskparser import use_kwargs
from run4it.api.user.model import User
from run4it.app.database import db

#class UserRegistrationSchema(Schema):
#    username = fields.String(required=True, validate=[validate.Length(min=4, max=16)], error_messages={'required': 'Username is required.'})
#    email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
#    password = fields.String(load_only=True, required=True, validate=[validate.Length(min=6, max=32)], error_messages={'required': 'Password is required.'})

class Register(Resource):

    reg_args = {
        "username": fields.String(required=True, validate=[validate.Length(min=4, max=16)], error_messages={'required': 'Username is required.'}),
        "email": fields.Email(required=True, error_messages={'required': 'Email is required.'}),
        "password": fields.String(load_only=True, required=True, validate=[validate.Length(min=6, max=32)], error_messages={'required': 'Password is required.'})
    }

    @use_kwargs(reg_args)
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

        return {
            "username": new_user.username,
            "email": new_user.email,
            "token": access_token,
            "refresh_token": refresh_token}, 201
