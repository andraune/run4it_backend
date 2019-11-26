#import datetime as dt
from flask_restful import Resource, request
#from flask_apispec import use_kwargs, marshal_with
#from flask_jwt_extended import (create_access_token, create_refresh_token,
#                                jwt_required, jwt_refresh_token_required,
#                                get_jwt_identity, get_raw_jwt)

#from run4it.app.database import db
#from run4it.api.exceptions import report_error_and_abort
from .model import Profile
#from .schema import user_schema, confirmation_schema, login_schema


class Profile(Resource):
	#@marshal_with(user_schema)
	def get(self, username):
    	# load profile from db
		return username, 200
