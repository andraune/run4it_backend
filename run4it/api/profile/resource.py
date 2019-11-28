import datetime as dt
from flask_restful import Resource, request
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from .model import Profile
from .schema import profile_schema


class Profile(Resource):
	@jwt_required
	@marshal_with(profile_schema)
	def get(self, username):
    	
		
		# load profile from db
		return { "username" : username }, 200
