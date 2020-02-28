import datetime as dt
from run4it.app.database import (
	Column, SurrogatePK, TimestampedModel, Model, db, reference_col, relationship)




class Profile(SurrogatePK, TimestampedModel):
	__tablename__ = 'user_profiles'

	# id required for primary join
	id = Column(db.Integer, primary_key=True, index=True)
	height = Column(db.Integer, nullable=True)
	weight = Column(db.Float, nullable=True)
	birth_date = Column(db.Date, nullable=True)

	user_id = reference_col('users', unique=True, nullable=False, index=True)
	user = relationship('User', backref=db.backref('profile', uselist=False))
	weights = relationship('ProfileWeightHistory', lazy='dynamic')
	goals = relationship('Goal', lazy='dynamic')

	def __init__(self, user, weights=[], **kwargs):
		db.Model.__init__(self, user=user, weights=weights, **kwargs)

	def set_height(self, height):
		if height > 0:
			self.height = height
		else:
			self.height = None
	
	def set_weight(self, weight):
		if weight > 0.0:
			self.weight = weight
			weight_history_record = ProfileWeightHistory(weight=weight)
			self.weights.append(weight_history_record)
			weight_history_record.save(False)
		else:
			self.weight = None

	def set_birth_date(self, year, month, day):
		self.birth_date = dt.date(year, month, day)

	@property
	def username(self):
		return self.user.username

	def __repr__(self):
		return '<UserProfile({username!r})>'.format(username=self.username)


class ProfileWeightHistory(SurrogatePK, Model):
	__tablename__ = 'profile_weight_history'

	id = Column(db.Integer, primary_key=True, index=True)
	profile_id = reference_col('user_profiles')
	weight = Column(db.Float())
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
