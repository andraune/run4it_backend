from run4it.app.database import Column, SurrogatePK, db


class Script(SurrogatePK, db.Model):
	__tablename__ = 'scripts'
	name = Column(db.String(64), unique=True, nullable=False)
	started_at = Column(db.DateTime, nullable=True)
	completed_at = Column(db.DateTime, nullable=True)
	return_code = Column(db.Integer, nullable=True)

	def __init__(self, name):
		db.Model.__init__(self, name=name)

	@classmethod
	def find_by_name(cls, name):
		return cls.query.filter_by(name=name).first()

	@property
	def execution_time(self):
		if self.started_at is not None and self.completed_at is not None:
			return self.completed_at - self.started_at
		return None

	def __repr__(self):
		return '<Script({name!r}:{last_run!r}:{ret_code!r})>'.format(
			name=self.name,
			last_run=self.completed_at.strftime("%Y-%m-%d %H:%M:%S"),
			ret_code=self.return_code)
