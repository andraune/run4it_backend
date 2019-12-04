from flask_restful import Resource
from flask_apispec import marshal_with
from webargs.flaskparser import use_kwargs
from run4it.app.database import db
from run4it.api.templates import report_error_and_abort
from .model import Discipline as DisciplineModel
from .schema import discipline_schema, disciplines_schema


class DisciplineList(Resource):
	@use_kwargs(discipline_schema, locations={"query"})
	@marshal_with(disciplines_schema)
	def get(self, limit=20, offset=0, **kwargs):			
		return DisciplineModel.query.order_by(DisciplineModel.length.asc()).\
			limit(limit).offset(offset).all()
