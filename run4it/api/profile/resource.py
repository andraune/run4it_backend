import datetime as dt
from flask_restful import Resource, request
from flask_apispec import use_kwargs, marshal_with
from flask_jwt_extended import (jwt_required
#                                get_jwt_identity, get_raw_jwt
)

#from run4it.api.exceptions import report_error_and_abort
from .model import Profile
from .schema import profile_schema


class Profile(Resource):
	@jwt_required
	@marshal_with(profile_schema)
	def get(self, username):
    	
		
		# load profile from db
		return { "username" : username }, 200
