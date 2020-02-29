import datetime as dt
from run4it.api.goal import GoalModel
from run4it.app.database import (
	Column, SurrogatePK, TimestampedModel, Model, db, reference_col, relationship)

from sqlalchemy import and_, or_




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

	@property
	def username(self):
		return self.user.username

	def get_active_goals(self, timestamp=dt.datetime.utcnow()):
		return self.goals.filter(and_(GoalModel.start_at <= timestamp), (GoalModel.end_at >= timestamp)).order_by(GoalModel.end_at.asc()).all()

	def get_expired_goals(self, timestamp=dt.datetime.utcnow()):
		return self.goals.filter(GoalModel.end_at <= timestamp).order_by(GoalModel.end_at.desc()).all()

	def get_future_goals(self, timestamp=dt.datetime.utcnow()):
		return self.goals.filter(GoalModel.start_at > timestamp).order_by(GoalModel.start_at.asc()).all()

	def get_completed_goals(self, timestamp=dt.datetime.utcnow()):
		return self.goals.filter(
			GoalModel.end_at <= timestamp,
			or_(and_(GoalModel.start_value < GoalModel.target_value, GoalModel.current_value >= GoalModel.target_value),
				and_(GoalModel.start_value > GoalModel.target_value, GoalModel.current_value <= GoalModel.target_value))
			).order_by(GoalModel.end_at.desc()).all()

	def get_incompleted_goals(self, timestamp=dt.datetime.utcnow()):
		return self.goals.filter(
			GoalModel.end_at <= timestamp,
			or_(and_(GoalModel.start_value < GoalModel.target_value, GoalModel.current_value < GoalModel.target_value),
				and_(GoalModel.start_value > GoalModel.target_value, GoalModel.current_value > GoalModel.target_value))
			).order_by(GoalModel.end_at.desc()).all()

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

	def __repr__(self):
		return '<UserProfile({username!r})>'.format(username=self.username)


class ProfileWeightHistory(SurrogatePK, Model):
	__tablename__ = 'profile_weight_history'

	id = Column(db.Integer, primary_key=True, index=True)
	profile_id = reference_col('user_profiles')
	weight = Column(db.Float())
	created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
