import ntpath
from math import floor
from sqlalchemy import and_
from run4it.app.database import Column, SurrogatePK, reference_col, relationship, db
from .gpx import GpxParser
from .tcx import TcxParser


def is_filename_extension_of_type(filename, extension):
	if filename is not None and filename != "":
		return "." in filename and filename.rsplit('.', 1)[1].lower() == extension
	else:
		return False

class WorkoutCategory(SurrogatePK, db.Model):
	__tablename__ = 'workout_categories'
	id = Column(db.Integer, primary_key=True, index=True)
	name = Column(db.String(32), nullable=False, unique=True)
	supports_gps_data = Column(db.Boolean, nullable=False)

	def __init__(self, name, supports_gps_data):
		db.Model.__init__(self, name=name, supports_gps_data=supports_gps_data)

	@classmethod
	def find_by_name(cls, name):
		return cls.query.filter_by(name=name).first()

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

	def register_extended_data(self):
		self.extended_track_data = None
		self.extended_split_data = None
		self.extended_summary = None
		# parse file if it exists
		if is_filename_extension_of_type(self.resource_path, "gpx"):
			gpx = GpxParser(self.resource_path)
			if gpx.get_num_of_tracks() > 0:
				self.extended_track_data, self.extended_split_data, self.extended_summary = gpx.get_track_data(1) # we only expect one track per file
		elif is_filename_extension_of_type(self.resource_path, "tcx"):
			tcx = TcxParser(self.resource_path)
			if tcx.get_num_of_tracks() > 0:
				self.extended_track_data, self.extended_split_data, self.extended_summary = tcx.get_track_data()
		if not self.category.supports_gps_data:
			self.extended_track_data = None
			self.extended_split_data = None

	@property
	def resource_file(self):
		if self.resource_path is not None:
			return ntpath.basename(self.resource_path)
		else:
			return None

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

	@classmethod
	def get_workouts_for_goal(cls, goal):
		if goal.category.workout_category is not None:
			goal_workout_id = goal.category.workout_category.id
			return cls.query.filter(and_(
				Workout.category_id==goal_workout_id,
				Workout.profile_id==goal.profile_id,
				Workout.start_at >= goal.start_at,
				Workout.start_at < goal.end_at)
				).order_by(Workout.start_at.asc()).all()
		else:
			return []

	def __repr__(self):
		return '<Workout({name!r},{distance!r}m)>'.format(
			name=self.name,
			distance=self.distance)
