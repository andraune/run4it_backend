from flask_restful import Resource
from flask_apispec import marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_kwargs
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from .model import Discipline as DisciplineModel
from .schema import discipline_schema, disciplines_schema, discipline_update_schema


class DisciplineList(Resource):
	@use_kwargs(discipline_schema, locations={"query"})
	@marshal_with(disciplines_schema)
	def get(self, limit=20, offset=0, **kwargs):			
		return DisciplineModel.query.order_by(DisciplineModel.length.asc()).\
			limit(limit).offset(offset).all()

	@jwt_required
	@use_kwargs(discipline_update_schema, error_status_code = 422)
	@marshal_with(discipline_schema)
	def post(self, name, length, **kwargs):
		auth_username = get_jwt_identity()

		discipline = DisciplineModel.find_by_name(name)

		if discipline is not None:
			report_error_and_abort(409, "discipline", "Discipline name already exists.")
		
		try:
			new_discipline = DisciplineModel(name, length, auth_username)
			new_discipline.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "discipline", "Unable to create discipline.")

		return new_discipline


class Discipline(Resource):
	pass
	
