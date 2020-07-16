from copy import copy as objcopy
from os import path
from geopy.distance import distance as geo_distance
from math import sqrt, floor
import gpxpy

import datetime as dt

SPEED_NO_MOVEMENT_LIMIT_M_PER_S = 0.5
ELEVATION_GAIN_IGNORE_LIMIT_M = 0.3
SPLIT_DISTANCE_M = 998 # in practice, we get approx ~1000m pr split

class WorkoutDataPoint:
	
	def __init__(self, latitude, longitude, elevation, time, duration, distance, avg_speed, heart_bpm=0):
		self.latitude = round(latitude, 6) # decimal degrees
		self.longitude = round(longitude, 6)  # decimal degrees
		self.elevation = round(elevation, None) # meter
		self.time = time
		self.duration = round(duration, 1) # seconds
		self.distance = round(distance, 1) # meters
		self.average_speed = round(avg_speed, 1)
		self.heart_bpm = round(heart_bpm, None)
	
	@property
	def average_pace(self):
		if self.average_speed > 0.0:
			pace_float = 60.0 / self.average_speed
			pace_min = floor(pace_float)
			pace_sec = int((pace_float - pace_min) * 60)
			return "{0:02d}:{1:02d}".format(pace_min, pace_sec)
		else:
			return ""

	def __repr__(self):
		return '<WorkoutDataPoint({time!r}s, {dist!r}m, {speed!r}kmh>'.format(time=self.duration, dist=self.distance, speed=self.average_speed)


class GpxParser:
	def __init__(self, filename):
		self.gpx_filepath = None
		self.gpx_data = None

		if filename is not None and len(filename) > 0:
			self.gpx_filepath = filename

		if self.gpx_filepath is not None:
			try:
				gpx_file = open(self.gpx_filepath, 'r')
				self.gpx_data = gpxpy.parse(gpx_file)
				gpx_file.close()
			except:
				self.gpx_data = None

		if self.gpx_data is not None and len(self.gpx_data.tracks) == 0:
			self.gpx_data = None

	def get_num_of_tracks(self):
		if self.gpx_data is not None:
			return len(self.gpx_data.tracks)
		else:
			return 0
	
	def get_track_data(self, track_no):
		if track_no > 0 and track_no <= self.get_num_of_tracks():
			track_raw_data = self.gpx_data.tracks[track_no - 1]
			points = self._get_segments_points(track_raw_data.segments)
			return self._process_track_points(points)
		else:
			return None, None, None

	def _process_track_points(self, points):
		track_data = list()
		split_data = list()
		summary = None
		cumulative_duration = 0.0
		cumulative_distance = 0.0
		cumulative_elevation_gain = 0.0
		start_dist_current_split = 0
		start_dur_current_split = 0
		start_ele_current_split = 0

		for idx in range(len(points)):
			if idx == 0:
				track_data.append(WorkoutDataPoint(points[idx].latitude, points[idx].longitude, points[idx].elevation, points[idx].time, 0, 0, 0))
				start_ele_current_split = track_data[0].elevation
			else:
				point = points[idx]
				previous_point = points[idx-1]
				# duration			
				time_diff = round((point.time - previous_point.time).total_seconds(), 1)
				cumulative_duration += time_diff		
				# distance
				elevation_diff = floor(point.elevation - previous_point.elevation)
				distance_diff_2d = geo_distance((previous_point.latitude, previous_point.longitude), (point.latitude, point.longitude)).m
				cumulative_distance += sqrt(distance_diff_2d**2 + (elevation_diff)**2)
				# speed & elevation gain, slightly averaged
				avg_speed_kmh = 0
				if idx > 4:
					previous_point5 = points[idx-5]
					speed_elevation_diff = floor(point.elevation - previous_point5.elevation)
					speed_time_diff = round((point.time - previous_point5.time).total_seconds(), 1)
					speed_dist_diff_2d = geo_distance((previous_point5.latitude, previous_point5.longitude), (point.latitude, point.longitude)).m
					speed_dist_diff_3d = sqrt(speed_dist_diff_2d**2 + (speed_elevation_diff)**2)
					if (speed_elevation_diff / 5) > ELEVATION_GAIN_IGNORE_LIMIT_M:
						cumulative_elevation_gain += (speed_elevation_diff / 5)
					if speed_time_diff > 0:
						avg_speed_kmh = 3.6 * speed_dist_diff_3d / speed_time_diff
				# add record
				track_data.append(WorkoutDataPoint(point.latitude, point.longitude, point.elevation, point.time, cumulative_duration, cumulative_distance, avg_speed_kmh))
				# splits
				if cumulative_distance-start_dist_current_split >= SPLIT_DISTANCE_M or idx == (len(points)-1):
					split_point = objcopy(track_data[-1])
					split_point.distance -= start_dist_current_split
					split_point.duration -= start_dur_current_split
					split_point.elevation -= start_ele_current_split
					if split_point.duration > 0:
						split_point.average_speed = 3.6 * split_point.distance / split_point.duration
					else:
						split_point.average_speed = 0.0
					split_data.append(split_point)
					start_dist_current_split = cumulative_distance
					start_dur_current_split = cumulative_duration
					start_ele_current_split = track_data[-1].elevation
				
				# hack to set speed for first records
				if idx == 5:
					track_data[0].average_speed = track_data[5].average_speed
					track_data[1].average_speed = track_data[5].average_speed
					track_data[2].average_speed = track_data[5].average_speed
					track_data[3].average_speed = track_data[5].average_speed
					track_data[4].average_speed = track_data[5].average_speed
		# summary
		if len(track_data) > 0:
			# summary contains: start lat./long., total elevation gain, total duration, total distance, avg speed
			first_point = points[0]
			last_track_data = track_data[-1]
			total_avg_speed_kmh = 3.6 * last_track_data.distance / last_track_data.duration
			summary = WorkoutDataPoint(first_point.latitude, first_point.longitude, cumulative_elevation_gain, first_point.time, last_track_data.duration, last_track_data.distance, total_avg_speed_kmh)
		
		return track_data, split_data, summary



	def _get_segments_points(self, segments_raw_data):
		return_points = []
		for segment_raw_data in segments_raw_data:
			segment_points = segment_raw_data.points
			return_points += segment_points
		
		# remove points in both ends of array if movement is very low
		start_idx = self._find_movement_start(return_points)
		end_idx = self._find_movement_end(return_points)
		num_points = len(return_points)

		if end_idx <= start_idx:
			return_points = []

		if end_idx < (num_points-1):
			return_points = return_points[:end_idx]

		if start_idx > 0:
			return_points = return_points[start_idx:]

		return return_points
	
	def _find_movement_start(self, points):
		i=1
		while i < len(points):
			p1 = points[i-1]
			p2 = points[i]
			dist = geo_distance((p1.latitude, p1.longitude),(p2.latitude,p2.longitude)).m
			time = (p2.time - p1.time).total_seconds()
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i+=1
		return i-1
	
	def _find_movement_end(self, points):
		i=len(points)-1
		while i > 0:
			p1 = points[i-1]
			p2 = points[i]
			dist = geo_distance((p1.latitude, p1.longitude),(p2.latitude,p2.longitude)).m
			time = (p2.time - p1.time).total_seconds()
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i-=1

		return i

	def __repr__(self):
		return '<GpxParser({file!r}, {tracks!r}>'.format(file=self.gpx_filepath, tracks=self.get_num_of_tracks())


if __name__ == "__main__":
	current_path = path.abspath(path.dirname(__file__))
	test_file_path1 = path.abspath(path.join(current_path, "..", "..", "..", "test.gpx")) #polar
	test_file_path2 = path.abspath(path.join(current_path, "..", "..", "..", "test_garmin.gpx"))

	parsers = list()
	parsers.append(GpxParser(test_file_path1))
	parsers.append(GpxParser(test_file_path2))

	print("GPX PARSER")

	for i in range(len(parsers)):
		gpx = parsers[i]
		num_tracks = gpx.get_num_of_tracks()
		if num_tracks == 0:
			print("GPX parse failed")
			exit()
		
		print("GPX parsed,", num_tracks, "track(s) found.")

		start_get_track_data = dt.datetime.utcnow()
		track_data, track_splits, track_summary = gpx.get_track_data(1)
		end_get_track_data = dt.datetime.utcnow()

		print()
		print("Get track data took", (end_get_track_data-start_get_track_data).total_seconds(), "s")
		print()

		if track_data is None or track_splits is None or track_summary is None:
			print("Failed to get track data for track 1")
			exit()
		
		print("Parse returned", len(track_data), "points")

		print()
		print("SPLITS:")
		for i in range(len(track_splits)):
			if track_splits[i] is not None:
				print("Split {0:2d}: {1:02d}:{2:02d}, {3} min/km, {4}m".format(
					i+1,
					int(track_splits[i].duration/60),
					int(track_splits[i].duration%60),
					track_splits[i].average_pace,
					track_splits[i].elevation))

		print()
		print("TRACK SUMMARY:")
		print("Start position lat/long:", track_summary.latitude, ",", track_summary.longitude)
		print("Elevation gain:", track_summary.elevation, "m")
		
		if (track_summary.duration >= 3600.0):
			print("Duration: {0:02d}h {1:02d}min {2:02d}s".format(floor(track_summary.duration/3600), int(track_summary.duration%3600/60), int(track_summary.duration/60%60)))
		else:
			print("Duration: {0:02d}min {1:02d}s".format(int(track_summary.duration/60), int(track_summary.duration%60)))

		print("Distance:", round(track_summary.distance/1000.0, 2), "km")
		print("Avg speed:", track_summary.average_speed, "km/h")
		print("Avg pace:", track_summary.average_pace, "min/km")
		print("Time:", track_summary.time)
