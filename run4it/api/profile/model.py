import datetime as dt
from run4it.app.database import (
	Column, SurrogatePK, TimestampedModel, db, reference_col, relationship)


class Profile(SurrogatePK, TimestampedModel):
	__tablename__ = 'user_profiles'

	# id required for primary join
	id = Column(db.Integer, primary_key=True, index=True)
	height = Column(db.Integer, nullable=True)
	birth_date = Column(db.Date, nullable=True)

	user_id = reference_col('users', unique=True, nullable=False, index=True)
	user = relationship('User', backref=db.backref('profile', uselist=False))

	def __init__(self, user, **kwargs):
		db.Model.__init__(self, user=user, **kwargs)

	def set_height(self, height):
		if height > 0:
			self.height = height
		else:
			self.height = None

	def set_birth_date(self, year, month, day):
		self.birth_date = dt.date(year, month, day)

	@property
	def username(self):
		return self.user.username

	def __repr__(self):
		return '<UserProfile({username!r})>'.format(username=self.username)
