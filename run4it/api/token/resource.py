"""API Resources for handling user tokens."""
import datetime as dt
from flask import jsonify
from flask_restful import Resource
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from flask_jwt_extended import fresh_jwt_required, jwt_required, get_jwt_identity

from run4it.app.database import db
from run4it.api.templates import generate_message_response, report_error_and_abort
from .model import TokenRegistry
from .schema import token_schema, tokens_schema, token_update_schema


class TokenList(Resource):
	@jwt_required
	@marshal_with(tokens_schema)
	def get(self, **kwargs):
		auth_username = get_jwt_identity()
		user_tokens = TokenRegistry.find_by_username(auth_username)
		return user_tokens, 200

class Token(Resource):
	@jwt_required
	@marshal_with(token_schema)
	def get(self, token_id, **kwargs):
		auth_username = get_jwt_identity()
		user_token = TokenRegistry.get_by_id(token_id)

		if user_token is None:
			report_error_and_abort(404, "token", "Token not found.")

		if user_token.username != auth_username:
			report_error_and_abort(403, "token", "Other user's token requested.")

		return user_token

	
	@fresh_jwt_required
	@use_kwargs(token_update_schema)
	@marshal_with(token_schema)
	def put(self, token_id, revoked, **kwargs):
		auth_username = get_jwt_identity()
		user_token = TokenRegistry.get_by_id(token_id)

		if user_token is None:
			report_error_and_abort(404, "token", "Token not found.")

		if user_token.username != auth_username:
			report_error_and_abort(403, "token", "Cannot update other user's token.")

		try:
			user_token.revoked = revoked
			user_token.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "profile", "Unable to update token")

		return user_token


	@fresh_jwt_required
	def delete(self, token_id, **kwargs):
		auth_username = get_jwt_identity()
		user_token = TokenRegistry.get_by_id(token_id)

		if user_token is None:
			report_error_and_abort(404, "token", "Token not found.")

		if user_token.username != auth_username:
			report_error_and_abort(403, "token", "Cannot delete other user's token.")

		try:
			user_token.delete()
		except:
			db.session.rollback()
			report_error_and_abort(500, "profile", "Unable to delete profile")			

		return generate_message_response(200, "token", "Token deleted.")
