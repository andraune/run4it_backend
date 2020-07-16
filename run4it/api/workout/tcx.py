from copy import copy as objcopy
from os import path
import datetime as dt
import json
from geopy.distance import distance as geo_distance
from math import sqrt, floor
from ggps import TcxHandler
from .gpx import WorkoutDataPoint


SPEED_NO_MOVEMENT_LIMIT_M_PER_S = 0.5
ELEVATION_GAIN_IGNORE_LIMIT_M = 0.1
SPLIT_DISTANCE_M = 997 # in practice, we get approx ~1000m pr split


class TcxParser:
	def __init__(self, filename):
		self.tcx_filepath = None
		self.tcx_data = None

		if filename is not None and len(filename) > 0:
			self.tcx_filepath = filename

		if self.tcx_filepath is not None:
			try:
				parser = TcxHandler()
				parser.parse(self.tcx_filepath)
				self.tcx_data = parser.trackpoints
				self._strip_ends_for_no_movement_tracks()
			except:
				self.tcx_data = None

		if self.tcx_data is not None and len(self.tcx_data) == 0:
			self.tcx_data = None

	def get_num_of_tracks(self):
		if self.tcx_data is not None:
			return len(self.tcx_data)
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

			for idx in range(len(self.tcx_data)):
				if idx == 0:
					point = json.loads(repr(self.tcx_data[idx]))
					elevation = 0.0 if "altitudemeters" not in point else float(point["altitudemeters"])
					time = dt.datetime.strptime(point["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
					heart_bpm = 0 if "heartratebpm" not in point else int(point["heartratebpm"])
					if heart_bpm > 0:
						cumulative_heart_bpm += heart_bpm
						heart_rate_points += 1
					
					track_data.append(WorkoutDataPoint(
						float(point["latitudedegrees"]),
						float(point["longitudedegrees"]),
						elevation,
						time,
						0, 0, 0,
						heart_bpm))
					start_ele_current_split = round(elevation, None)
				else:
					point = json.loads(repr(self.tcx_data[idx]))
					previous_point = json.loads(repr(self.tcx_data[idx-1]))
					# duration
					time = 	dt.datetime.strptime(point["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
					time_previous = dt.datetime.strptime(previous_point["time"], "%Y-%m-%dT%H:%M:%S.%fZ")		
					time_diff = round((time - time_previous).total_seconds(), 1)
					cumulative_duration += time_diff
					# distance
					elevation = 0.0 if "altitudemeters" not in point else float(point["altitudemeters"])
					elevation_previous = 0.0 if "altitudemeters" not in previous_point else float(previous_point["altitudemeters"])
					elevation_diff = floor(elevation - elevation_previous)
					latitude = float(point["latitudedegrees"])
					longitude = float(point["longitudedegrees"])
					latitude_previous = float(previous_point["latitudedegrees"])
					longitude_previous = float(previous_point["longitudedegrees"])
					distance_diff_2d = geo_distance((latitude_previous, longitude_previous), (latitude, longitude)).m
					cumulative_distance += sqrt(distance_diff_2d**2 + (elevation_diff)**2)
					#heart rate
					heart_bpm = 0 if "heartratebpm" not in point else int(point["heartratebpm"])
					if heart_bpm > 0:
						cumulative_heart_bpm += heart_bpm
						heart_rate_points += 1
					# speed & elevation gain, slightly averaged
					avg_speed_kmh = 0
					if idx > 4:
						previous_point5 = json.loads(repr(self.tcx_data[idx-5]))
						elevation_previous5 = 0.0 if "altitudemeters" not in previous_point5 else float(previous_point5["altitudemeters"])
						latitude_previous5 = float(previous_point5["latitudedegrees"])
						longitude_previous5 = float(previous_point5["longitudedegrees"])
						speed_elevation_diff = floor(elevation - elevation_previous5)
						speed_time_diff = round((time - dt.datetime.strptime(previous_point5["time"], "%Y-%m-%dT%H:%M:%S.%fZ")).total_seconds(), 1)
						speed_dist_diff_2d = geo_distance((latitude_previous5, longitude_previous5), (latitude, longitude)).m
						speed_dist_diff_3d = sqrt(speed_dist_diff_2d**2 + (speed_elevation_diff)**2)
						if (speed_elevation_diff / 5) > ELEVATION_GAIN_IGNORE_LIMIT_M:
							cumulative_elevation_gain += (speed_elevation_diff / 5)
						if speed_time_diff > 0:
							avg_speed_kmh = 3.6 * speed_dist_diff_3d / speed_time_diff

					# add record
					track_data.append(WorkoutDataPoint(
						latitude,
						longitude,
						elevation,
						time,
						cumulative_duration,
						cumulative_distance,
						avg_speed_kmh,
						heart_bpm))
					# splits
					if cumulative_distance-start_dist_current_split >= SPLIT_DISTANCE_M or idx == (len(self.tcx_data)-1):
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
		else:
			return None, None, None

	def _strip_ends_for_no_movement_tracks(self):
		if self.tcx_data is not None and len(self.tcx_data) > 0:
			# remove points in both ends of array if movement is very low
			start_idx = self._find_movement_start(self.tcx_data)
			end_idx = self._find_movement_end(self.tcx_data)
			num_points = len(self.tcx_data)

			if end_idx <= start_idx:
				self.tcx_data = []

			if end_idx < (num_points-1):
				self.tcx_data = self.tcx_data[:end_idx]

			if start_idx > 0:
				self.tcx_data = self.tcx_data[start_idx:]
	
	def _find_movement_start(self, points):
		i=1
		while i < len(points):
			p1 = json.loads(repr(self.tcx_data[i-1]))
			p2 = json.loads(repr(self.tcx_data[i]))
			time1 = dt.datetime.strptime(p1["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
			time2 = dt.datetime.strptime(p2["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
			time = (time2 - time1).total_seconds()
			latitude1 = float(p1["latitudedegrees"])
			longitude1 = float(p1["longitudedegrees"])
			latitude2 = float(p2["latitudedegrees"])
			longitude2 = float(p2["longitudedegrees"])
			dist = geo_distance((latitude1, longitude1),(latitude2, longitude2)).m
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i+=1
		return i-1
		
	def _find_movement_end(self, points):
		i=len(points)-1
		while i > 0:
			p1 = json.loads(repr(self.tcx_data[i-1]))
			p2 = json.loads(repr(self.tcx_data[i]))
			time1 = dt.datetime.strptime(p1["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
			time2 = dt.datetime.strptime(p2["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
			time = (time2 - time1).total_seconds()
			latitude1 = float(p1["latitudedegrees"])
			longitude1 = float(p1["longitudedegrees"])
			latitude2 = float(p2["latitudedegrees"])
			longitude2 = float(p2["longitudedegrees"])
			dist = geo_distance((latitude1, longitude1),(latitude2, longitude2)).m
			if time>0:
				speed = dist/time
				if speed > SPEED_NO_MOVEMENT_LIMIT_M_PER_S:
					break
			i-=1

		return i			

	def __repr__(self):
		return '<TcxParser({file!r}, {tracks!r}>'.format(file=self.tcx_filepath, tracks=self.get_num_of_tracks())


if __name__ == "__main__":
	current_path = path.abspath(path.dirname(__file__))
	test_file_path_tcx1 = path.abspath(path.join(current_path, "..", "..", "..", "test.tcx")) #polar
	test_file_path_tcx2 = path.abspath(path.join(current_path, "..", "..", "..", "test_garmin.tcx"))

	parsers = list()
	parsers.append(TcxParser(test_file_path_tcx1))
	parsers.append(TcxParser(test_file_path_tcx2))

	print("TCX PARSER")

	for i in range(len(parsers)):
		parser = parsers[i]
		num_tracks = parser.get_num_of_tracks()

		if num_tracks == 0:
			print("TCX parse failed.")
			continue
		
		start_get_track_data = dt.datetime.utcnow()
		track_data, track_splits, track_summary = parser.get_track_data()
		end_get_track_data = dt.datetime.utcnow()

		print()
		print("Get track data took", (end_get_track_data-start_get_track_data).total_seconds(), "s")
		print()	

		if track_data is None or track_splits is None or track_summary is None:
			print("Failed to get track data")
			continue

		print("Parse returned", len(track_data), "points")


		print("TRACK DATA:")
		for i in range(5):
			if track_data[i+40] is not None:
				print(track_data[i+40])
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
		print("Avg BPM:", track_summary.heart_bpm)
		print("Time:", track_summary.time)
