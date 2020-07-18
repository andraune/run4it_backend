from run4it.app.database import Column, SurrogatePK, TimestampedModel, db


class Discipline(SurrogatePK, db.Model):
	__tablename__ = 'disciplines'

	name = Column(db.String(128), unique=True, nullable=False, index=True)
	length = Column(db.Integer, nullable=False)
	username = Column(db.String(16), nullable=True)
	is_route = Column(db.Boolean, nullable=False)

	def __init__(self, name, length, username=None, is_route=False):
		db.Model.__init__(self, name=name, length=length, username=username, is_route=is_route)

	@classmethod
	def find_by_name(cls, name):
		return cls.query.filter_by(name=name).first()

	def __repr__(self):
		return '<Discipline({name!r})>'.format(name=self.name)
