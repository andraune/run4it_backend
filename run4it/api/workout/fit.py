from copy import copy as objcopy
from os import path
from geopy.distance import distance as geo_distance
from math import sqrt, floor
import fitparse
import datetime as dt
from .gpx import WorkoutDataPoint

SPEED_NO_MOVEMENT_LIMIT_M_PER_S = 0.5
ELEVATION_GAIN_IGNORE_LIMIT_M = 0.1
SPLIT_DISTANCE_M = 998 # in practice, we get approx ~1000m pr split


class FitParser:
	def __init__(self, filename):
		self.fit_filepath = None
		self.fit_data = []
		if filename is not None and len(filename) > 0:
			self.fit_filepath = filename
			try:
				fit_file = fitparse.FitFile(self.fit_filepath)
				for record in fit_file.get_messages("record"):
					point = self._get_record_data(record)
					if point is not None:
						self.fit_data.append(point)
			except:
				self.fit_data = None
		if self.get_num_of_tracks() > 0:
			self._strip_ends_for_no_movement_tracks()

	def get_num_of_tracks(self):
		if self.fit_data is not None:
			return len(self.fit_data)
		else:
			return 0
	
	def get_track_data(self):
		if self.get_num_of_tracks() > 0:
			track_data = list()
			split_data = list()
			summary = None
			cumulative_duration = 0.0
			cumulative_distance = 0.0
			cumulative_elevation_gain = 0.0
			cumulative_heart_bpm = 0.0
			heart_rate_points = 0
			start_dist_current_split = 0
			start_dur_current_split = 0
			start_ele_current_split = 0

			for idx in range(len(self.fit_data)):
				if idx == 0:
					point = self.fit_data[idx]
					if point['heart_rate'] > 0:
						cumulative_heart_bpm += point['heart_rate']
						heart_rate_points += 1
					track_data.append(WorkoutDataPoint(
						point["latitude"],
						point["longitude"],
						point["elevation"],
						point["time"],
						0, 0, 0,
						point['heart_rate']))
					start_ele_current_split = point["elevation"]
				else:
					point = self.fit_data[idx]
					previous_point = self.fit_data[idx-1]
					# duration
					time_diff = round((point['time'] - previous_point['time']).total_seconds(), 1)
					cumulative_duration += time_diff
					# distance
					elevation_diff = floor(point['elevation'] - previous_point['elevation'])
					distance_diff_2d = geo_distance((previous_point['latitude'], previous_point['longitude']), (point['latitude'], point['longitude'])).m
					cumulative_distance += sqrt(distance_diff_2d**2 + (elevation_diff)**2)
					# heart rate
					if point['heart_rate'] > 0:
						cumulative_heart_bpm += point['heart_rate']
						heart_rate_points += 1
					# speed & elevation gain, slightly averaged
					avg_speed_kmh = 0
					if idx > 4:
						previous_point5 = self.fit_data[idx-5]
						speed_elevation_diff = floor(point['elevation'] - previous_point5['elevation'])
						speed_time_diff = round((point['time'] - previous_point5['time']).total_seconds(), 1)
						speed_dist_diff_2d = geo_distance((previous_point5['latitude'], previous_point5['longitude']), (point['latitude'], point['longitude'])).m
						speed_dist_diff_3d = sqrt(speed_dist_diff_2d**2 + (speed_elevation_diff)**2)
						if (speed_elevation_diff / 5) > ELEVATION_GAIN_IGNORE_LIMIT_M:
							cumulative_elevation_gain += (speed_elevation_diff / 5)
						if speed_time_diff > 0:
							avg_speed_kmh = 3.6 * speed_dist_diff_3d / speed_time_diff
					# add record										
					track_data.append(WorkoutDataPoint(
						point["latitude"],
						point["longitude"],
						point["elevation"],
						point["time"],
						cumulative_duration,
						cumulative_distance,
						avg_speed_kmh,
						point['heart_rate']))
					# splits
					if cumulative_distance-start_dist_current_split >= SPLIT_DISTANCE_M or idx == (len(self.fit_data)-1):
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
				first_point = track_data[0]
				last_point = track_data[-1]
				total_avg_speed_kmh = 3.6 * last_point.distance / last_point.duration
				avg_heart_rate = 0
				if heart_rate_points > 0:
					avg_heart_rate = cumulative_heart_bpm / heart_rate_points
				summary = WorkoutDataPoint(first_point.latitude, first_point.longitude, cumulative_elevation_gain, first_point.time, last_point.duration, last_point.distance, total_avg_speed_kmh, avg_heart_rate)

			return track_data, split_data, summary
		
		else: # no tracks
			return None, None, None


	def _strip_ends_for_no_movement_tracks(self):
		if self.get_num_of_tracks() > 0:
			num_points = len(self.fit_data)
			start_idx = self._find_movement_start(self.fit_data)
			end_idx = self._find_movement_end(self.fit_data)

			if end_idx <= start_idx:
				self.fit_data = []
			if end_idx < (num_points - 1):
				self.fit_data = self.fit_data[:end_idx]
			if start_idx > 0:
				self.fit_data = self.fit_data[start_idx:]


	def _find_movement_start(self, points):
		i=1
		while i < len(points):
			p1 = self.fit_data[i-1]
			p2 = self.fit_data[i]
			time = (p2["time"] - p1["time"]).total_seconds()
			dist = geo_distance((p1["latitude"], p1["longitude"]),(p2["latitude"], p2["longitude"])).m
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i+=1
		return i-1


	def _find_movement_end(self, points):
		i=len(points)-1
		while i > 0:
			p1 = self.fit_data[i-1]
			p2 = self.fit_data[i]
			time = (p2["time"] - p1["time"]).total_seconds()
			dist = geo_distance((p1["latitude"], p1["longitude"]),(p2["latitude"], p2["longitude"])).m
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i-=1
		return i


	def _get_record_data(self, record):
		ret_data = {"latitude": 0.0, "longitude": 0.0, "elevation": 0.0, "time": None, "heart_rate": 0 }

		# loop through data, and save the items we need
		for data in record:
			if data.name == "position_lat" and data.value is not None:
				if data.units == "semicircles":
					ret_data["latitude"] = round(float(data.value * 180 / 2**31), 6)
				elif data.units == "degrees":
					ret_data["latitude"] = round(float(data.value), 6)
			elif data.name == "position_long" and data.value is not None and data.units == "semicircles":
				if data.units == "semicircles":
					ret_data["longitude"] = round(float(data.value * 180 / 2**31), 6)
				elif data.units == "degrees":
					ret_data["longitude"] = round(float(data.value), 6)
			elif data.name == "altitude" and data.value is not None and data.units == "m":
				ret_data["elevation"] = round(data.value)
			elif data.name == "timestamp" and data.value is not None:
				ret_data["time"] = data.value
			elif data.name == "heart_rate" and data.value is not None:
				ret_data["heart_rate"] = data.value

		# Return if all data is found
		if (ret_data["latitude"] == 0.0 and ret_data["longitude"] == 0.0) or ret_data["time"] is None:
			return None
		return ret_data

	def __repr__(self):
		return '<FitParser({file!r}, {tracks!r}>'.format(file=self.fit_filepath, tracks=self.get_num_of_tracks())


if __name__ == "__main__":
	current_path = path.abspath(path.dirname(__file__))
	test_file_path1 = path.abspath(path.join(current_path, "..", "..", "..", "test_polar.fit"))
	test_file_path2 = path.abspath(path.join(current_path, "..", "..", "..", "test_garmin.fit"))

	parsers = list()
	parsers.append(FitParser(test_file_path1))
	parsers.append(FitParser(test_file_path2))

	print("FIT PARSER")

	for i in range(len(parsers)):
		fit = parsers[i]
		num_tracks = fit.get_num_of_tracks()
		if num_tracks == 0:
			print("FIT parse failed - quitting")
			exit()
		
		print("FIT parsed,", num_tracks, "track(s) found.")
		start_get_track_data = dt.datetime.utcnow()
		track_data, track_splits, track_summary = fit.get_track_data()
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
