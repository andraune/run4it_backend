"""API Resources for handling user tokens."""
import datetime as dt
from flask_restful import Resource
from flask_apispec import marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity

from run4it.app.database import db
from run4it.api.exceptions import report_error_and_abort
from .model import TokenRegistry
from .schema import token_schema, tokens_schema


class TokenList(Resource):
	@jwt_required
	@marshal_with(tokens_schema)
	def get(self, **kwargs):
		auth_username = get_jwt_identity()
		user_tokens = TokenRegistry.find_by_username(auth_username)
		return user_tokens, 200
