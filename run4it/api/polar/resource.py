import datetime as dt
from os import path
from flask import current_app, render_template, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from run4it.api.templates import report_error_and_abort
from run4it.api.profile.auth_helper import get_auth_profile_or_abort
from run4it.api.user import User
from .model import PolarUser
from .schema import polar_callback_schema, polar_user_schema
from .polar import retrieve_access_token, register_user, unregister_user


class ProfilePolar(Resource):
	@jwt_required
	@marshal_with(polar_user_schema)
	def get(self, username):
		profile = get_auth_profile_or_abort(username, "polar")
		polar_user = profile.get_polar_data()

		if polar_user is None:
			return {}, 204  # no data

		if not polar_user.has_valid_access_token():
			polar_user.generate_state_code()
		else:
			polar_user.state = None

		try:
			polar_user.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "polar", "Failed to retrieve data.")            

		return polar_user

	@jwt_required
	@marshal_with(polar_user_schema)
	def post(self, username):
		profile = get_auth_profile_or_abort(username, "polar")
		polar_user = profile.get_polar_data()

		if polar_user is None:
			polar_user = PolarUser(profile.id, profile.username)

		if not polar_user.has_valid_access_token():
			polar_user.generate_state_code()
		else:
			polar_user.state = None		

		try:
			polar_user.updated_at = dt.datetime.utcnow()
			polar_user.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "polar", "Failed to retrieve data.")            

		return polar_user


class PolarAuthorizationCallback(Resource):
	'''
		This resource should only be called from Polar, as a response to Oauth login attempt
		from redirect in PolarAuthorizationRedirect resource. The returned response should be
		text/html, not json
	'''
	@use_kwargs(polar_callback_schema, locations={"query"}) # do not report error if missing
	def get(self, state="", code="", error=""):
		title = "Polar"
		class_name = "primary-color"
		error_str = ""
		content_str = ""
	
		if len(error) > 0:
			error_str = "Polar returned '{err}'".format(err=error)
		elif len(code) == 0:
			error_str = 'Authorization code missing'
		elif len(state) == 0:
			error_str = 'Authorization ID missing'

		# Load user if we can
		polar_user = None
		if len(state) > 0:
			polar_user = PolarUser.find_by_state_code(state)
		
		if polar_user is None:
			error_str = 'Authorization ID invalid'
		else:
			if error_str == "":
				# try to get access token
				token_response = retrieve_access_token(code)

				if token_response is not None:
					# set token, token_expiry and register user
					polar_user.access_token = token_response['access_token']
					polar_user.access_token_expires = dt.datetime.utcnow() + dt.timedelta(int(token_response['expires_in']))
					polar_user.polar_user_id = token_response['x_user_id']

					if register_user(polar_user.access_token, polar_user.member_id):
						content_str = 'Your Run4IT account was successfully connected to Polar!'
					else:
						error_str = 'Polar user registration failed'
				else:
					error_str = 'Failed to retrieve token'

			# save user as 'updated' to signal that we tried to authorize
			try:
				polar_user.state = None
				polar_user.save()
				content_str = 'Your Run4IT account was successfully connected to Polar!'
			except:
				error_str = 'Internal server error'

		if error_str != "":
			content_str = 'Failed to connect to Polar ({error})'.format(error=error_str)
			class_name = "warn-color"

		return unregister_user('token', 12321)
	
		
		
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template('callback.html', title=title, className=class_name, contentString=content_str), 200, headers)
