from flask_restful import request, Resource
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
	def post(self, name, length, is_route, **kwargs):
		auth_username = get_jwt_identity()
		discipline = DisciplineModel.find_by_name(name)

		if discipline is not None:
			report_error_and_abort(409, "discipline", "Discipline name already exists.")
		
		try:
			new_discipline = DisciplineModel(name, length, auth_username, is_route)
			new_discipline.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "discipline", "Unable to create discipline.")

		return new_discipline, 200, {'Location': '{}/{}'.format(request.path, new_discipline.id)}


class Discipline(Resource):
	@marshal_with(discipline_schema)
	def get(self, disc_id, **kwargs):
		discipline = DisciplineModel.get_by_id(disc_id)

		if discipline is None:
			report_error_and_abort(404, "discipline", "Discipline not found.")

		return discipline

	@jwt_required
	@use_kwargs(discipline_update_schema, error_status_code = 422)
	@marshal_with(discipline_schema)
	def put(self, disc_id, name, length, is_route, **kwargs):
		auth_username = get_jwt_identity()

		discipline = DisciplineModel.get_by_id(disc_id)

		if discipline is None:
			report_error_and_abort(404, "discipline", "Discipline not found.")
		
		if discipline.username != auth_username:
			report_error_and_abort(403, "discipline", "Cannot update other user's token.")

		try:
			discipline.name = name
			discipline.length = length
			discipline.is_route = is_route
			discipline.save()
		except:
			db.session.rollback()
			report_error_and_abort(500, "discipline", "Unable to update discipline.")
		
		return discipline

