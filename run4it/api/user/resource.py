"""API Resources for handling registration, login, logout etc."""
import datetime as dt
from flask_restful import Resource, request
from flask_apispec import marshal_with
from flask_jwt_extended import (create_access_token, create_refresh_token,
								jwt_required, jwt_refresh_token_required,
								get_jwt_identity, get_raw_jwt)

from webargs.flaskparser import use_kwargs
from run4it.app.database import db
from run4it.api.templates import generate_message_response, report_error_and_abort
from run4it.api.token.model import TokenRegistry
from run4it.api.profile.model import Profile
from .mail import mail_send_confirmation_code
from .model import User, UserConfirmation
from .schema import user_schema, confirmation_schema, login_schema


class UserResource(Resource):
	@jwt_required
	@marshal_with(user_schema)
	def get(self, **kwargs):
		auth_username = get_jwt_identity()
		user = User.find_by_username(auth_username)

		if user is None: # should not be possible as we are auth'ed
			report_error_and_abort(422, "user", "User not found")
		
		return user

class Register(Resource):
	@use_kwargs(user_schema, error_status_code = 422)
	@marshal_with(user_schema)
	def post(self, username, email, password, **kwargs):

		if User.find_by_username(username):
			report_error_and_abort(409, "register", "User already exists(1)")

		if User.find_by_email(email):
			report_error_and_abort(409, "register", "User already exists(2)")
	
		new_user = User(username, email, password, **kwargs)
		new_profile = Profile(new_user)
		confirmation = UserConfirmation(username, None, **kwargs)

		try:
			confirmation.save()
			new_user.save()
			new_profile.save()
			mail_send_confirmation_code(username, email, confirmation.code)

		except:
			db.session.rollback()
			report_error_and_abort(500, "register", "Unable to create user")

		return new_user, 201, {'Location': '{0}/{1}'.format(request.path, new_user.id) }


class Confirmation(Resource):
	CONFIRMATION_CODE_EXPIRY_S = 3600

	@use_kwargs(confirmation_schema, error_status_code = 422)
	@marshal_with(user_schema)
	def post(self, username, confirmation_code, **kwargs):

		user = User.find_by_username(username)

		if not user:
			report_error_and_abort(422, "confirmation", "Confirmation failed.")
		
		confirmation = UserConfirmation.find_by_username(username)
		
		if not confirmation:
			report_error_and_abort(422, "confirmation", "Confirmation failed.")

		if not confirmation.check_code(confirmation_code):
			report_error_and_abort(422, "confirmation", "Confirmation failed (invalid code)")

		if not confirmation.check_expiration(self.CONFIRMATION_CODE_EXPIRY_S):
			report_error_and_abort(422, "confirmation", "Confirmation failed (activation code expired)")

		# If we reach here we have a valid user and confirmation code
		try:
			confirmation.delete()
			user.confirmed = True
			user.updated_at = dt.datetime.utcnow()
			user.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "confirmation", "Unable to confirm user")

		return user, 200


class Login(Resource):
	@use_kwargs(login_schema, error_status_code = 422)
	@marshal_with(user_schema)
	def post(self, email, password, **kwargs):
		user = User.find_by_email(email)

		if user is None:
		   report_error_and_abort(401, "login", "Login failed") 

		if not user.confirmed:
			report_error_and_abort(401, "login", "Login failed")

		if not user.check_password(password):
			report_error_and_abort(401, "login", "Login failed")
			
		user.access_token = create_access_token(identity=user.username, fresh=True)
		user.refresh_token = create_refresh_token(identity=user.username)
		TokenRegistry.add_token(user.access_token)
		TokenRegistry.add_token(user.refresh_token)
		return user, 200   


class LoginFresh(Resource):
	# Same as login, but no refresh token created.
	# Used when we need to confirm user properly (before changing password etc.)
	@use_kwargs(login_schema, error_status_code = 422)
	@marshal_with(user_schema)
	def post(self, email, password, **kwargs):
		user = User.find_by_email(email)

		if user is None:
		   report_error_and_abort(401, "login", "Login failed") 

		if not user.confirmed:
			report_error_and_abort(401, "login", "Login failed")

		if not user.check_password(password):
			report_error_and_abort(401, "login", "Login failed")
		
		user.access_token = create_access_token(identity=user.username, fresh=True)
		TokenRegistry.add_token(user.access_token)
		return user, 200


class LoginRefresh(Resource): 
	@jwt_refresh_token_required
	@marshal_with(user_schema)
	def post(self):
		username = get_jwt_identity()
		user = User.find_by_username(username)

		if user is None:
			report_error_and_abort(401, "refresh", "Login refresh failed")
		
		user.access_token = create_access_token(identity=user.username, fresh=False)
		TokenRegistry.add_token(user.access_token)
		return user, 200


class Logout(Resource):
	@jwt_required
	def delete(self):
		jti = get_raw_jwt()["jti"]
		token = TokenRegistry.find_by_jti(jti)

		if token is not None:
			try:
				token.revoked = False
				token.save()
			except:
				db.session.rollback()
				report_error_and_abort(500, "logout", "Logout failed(1).")				

		return generate_message_response(200, "logout", "Logged out.")	


class LogoutRefresh(Resource):
	@jwt_refresh_token_required
	def delete(self):
		jti = get_raw_jwt()["jti"]
		token = TokenRegistry.find_by_jti(jti)

		if token is not None:
			try:
				token.revoked = False
				token.save()
			except:
				db.session.rollback()
				report_error_and_abort(500, "logout", "Logout failed(2).")				

		return generate_message_response(200, "logout", "Logged out.")
