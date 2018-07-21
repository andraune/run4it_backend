"""API Resources for handling registration, login, logout etc of users."""
from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_kwargs

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
    def post(self, username, email, password):
        return { "username": username, "email": email }, 201

