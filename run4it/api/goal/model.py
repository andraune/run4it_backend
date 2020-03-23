import datetime as dt
from run4it.app.database import Column, SurrogatePK, reference_col, relationship, db


class GoalCategory(SurrogatePK, db.Model):
	__tablename__ = 'training_goal_categories'
	id = Column(db.Integer, primary_key=True, index=True)
	name = Column(db.String(32), nullable=False, unique=True)
	unit = Column(db.String(16), nullable=True)

	def __init__(self, name, unit=None):
		db.Model.__init__(self, name=name, unit=unit)
	
	def __repr__(self):
		return '<GoalCategory({name!r})>'.format(name=self.name)

class Goal(SurrogatePK, db.Model):
	__tablename__ = 'training_goals'
	start_at = Column(db.DateTime, nullable=False)
	end_at = Column(db.DateTime, nullable=False)
	start_value = Column(db.Float, nullable=False)
	current_value = Column(db.Float, nullable=False)
	target_value = Column(db.Float, nullable=False)

	category_id = reference_col('training_goal_categories', nullable=False)
	category = relationship('GoalCategory')
	profile_id = reference_col('user_profiles', nullable=False, index=True)

	def __init__(self, profile_id, category, start_at=dt.datetime.utcnow(), end_at=dt.datetime.utcnow()+dt.timedelta(days=1), start_value=0, target_value=0, current_value=0):
		db.Model.__init__(self, profile_id=profile_id, category=category, start_at=start_at, end_at=end_at, start_value=start_value, current_value=current_value, target_value=target_value)

	@property
	def category_name(self):
		return self.category.name

	@property
	def category_unit(self):
		if (self.category.unit is not None):
			return self.category.unit
		return ''

	@property
	def duration(self):	# returns days as decimal number with four digits after the decimal point
		return (self.end_at - self.start_at).days + round((self.end_at - self.start_at).seconds/86400, 4)
		
	def __repr__(self):
		return '<Goal({year!r}-{month!r}-{day!r}:{duration!r})>'.format(
			duration=self.duration,
			year=self.start_at.year,
			month=self.start_at.month,
			day=self.start_at.day)
