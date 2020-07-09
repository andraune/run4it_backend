from math import floor
from run4it.app.database import Column, SurrogatePK, reference_col, relationship, db


class WorkoutCategory(SurrogatePK, db.Model):
	__tablename__ = 'workout_categories'
	id = Column(db.Integer, primary_key=True, index=True)
	name = Column(db.String(32), nullable=False, unique=True)

	def __init__(self, name):
		db.Model.__init__(self, name=name)
	
	def __repr__(self):
		return '<WorkoutCategory({name!r})>'.format(name=self.name)


class Workout(SurrogatePK, db.Model):
	__tablename__ = 'workouts'
	name = Column(db.String(128), nullable=False)
	start_at = Column(db.DateTime, nullable=False)
	distance = Column(db.Integer, nullable=False)
	duration = Column(db.Integer, nullable=False)
	climb = Column(db.Integer, nullable=False)
	resource_path = Column(db.String(255), unique=True, nullable=True)
	edited = Column(db.Boolean, nullable=False)

	category_id = reference_col('workout_categories', nullable=False)
	category = relationship('WorkoutCategory')
	profile_id = reference_col('user_profiles', nullable=False, index=True)

	def __init__(self, profile_id, category, name, start_at, distance, duration, climb, resource_path=None, edited=False):
		db.Model.__init__(self, profile_id=profile_id, category=category, name=name, start_at=start_at, distance=distance, duration=duration, climb=climb, resource_path=resource_path, edited=edited)

	@property
	def category_name(self):
		return self.category.name
	
	@property
	def average_speed(self):
		dist_km = self.distance / 1000.0
		dur_h = self.duration / 3600.0
		
		if dur_h > 0.0:
			return round(dist_km / dur_h, 2)
		else:
			return 0.0
	
	@property
	def average_pace(self):
		dist_km = self.distance / 1000.0
		dur_min = self.duration / 60.0

		if dist_km > 0.0:
			avg_pace = dur_min / dist_km
			avg_pace_min = floor(avg_pace)
			avg_pace_sec = int((avg_pace - avg_pace_min) * 60)
			return "{0:02d}:{1:02d}".format(avg_pace_min, avg_pace_sec)
		else:
			return ""

	def __repr__(self):
		return '<Workout({name!r},{distance!r}m)>'.format(
			name=self.name,
			distance=self.distance)
