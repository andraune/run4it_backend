import io
import os
import pytest
import datetime as dt
from flask import current_app
from run4it.api.workout import ProfileWorkoutListResource, ProfileWorkoutResource, ProfileWorkoutGpxResource, WorkoutModel, WorkoutCategoryModel
from .helpers import get_response_json, register_confirmed_user, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestProfileWorkoutListResource:

	def setup(self): # register some workouts
		cat1 = WorkoutCategoryModel('Running', True)
		cat1.save(commit=False)
		cat2 = WorkoutCategoryModel('Hiking', True)
		cat2.save()
		now = dt.datetime.utcnow()
		WorkoutModel(1, cat1, "Run 1", now - dt.timedelta(days=3), 3456, 201, 12, 'path/run1.gpx', False).save(commit=False)
		WorkoutModel(1, cat1, "Run 2", now - dt.timedelta(days=2), 4567, 234, 1, None, True).save(commit=False)
		WorkoutModel(1, cat2, "Hike 1", now - dt.timedelta(days=1), 12345, 2340, 1102, None, False).save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileWorkoutListResource, username="jonny")
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_workouts_not_logged_in(self, api, client):
		url = api.url_for(ProfileWorkoutListResource, username="jonny")
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_workouts_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutListResource, username="jonny")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 3)
		assert(response_json[0]['id'] == 3) # newest first
		assert(response_json[1]['id'] == 2)
		assert(response_json[2]['id'] == 1)

	def test_get_workouts_limit2(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutListResource, username="jonny", limit=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 3) # newest first
		assert(response_json[1]['id'] == 2)

	def test_get_workouts_limit2_offset1(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutListResource, username="jonny", limit=2, offset=1)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 2) # newest first
		assert(response_json[1]['id'] == 1)
	
	def test_get_workouts_values(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutListResource, username="jonny", limit=1, offset=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 1)
		assert(response_json[0]['startAt'] is not None)
		assert(response_json[0]['resourceFile'] == "run1.gpx")
		assert(response_json[0]['categoryName'] == "Running")
		assert(response_json[0]['duration'] == 201)
		assert(response_json[0]['distance'] == 3456)
		assert(response_json[0]['climb'] == 12)
		assert(response_json[0]['name'] == "Run 1")
		assert(response_json[0]['edited'] == False)
		assert(response_json[0]['averageSpeed'] > 0)
		assert(response_json[0]['averagePace'] is not None)

	def test_create_workout_not_logged_in(self, api, client):
		url = api.url_for(ProfileWorkoutListResource, username="jonny")
		response = client.post(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_create_workout_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileWorkoutListResource, username="creator")
		datetime_start = dt.datetime.utcnow()
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "name":"My run", "startAt":"{0}".format(startAt), "distance":1234, "duration":198, "categoryID":1, "edited":True }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 4)
		assert(response_json["name"] == "My run")
		assert(response_json["startAt"] == startAt)
		assert(response_json["distance"] == 1234)
		assert(response_json["duration"] == 198)
		assert(response_json["categoryName"] == "Running")
		assert(response_json["resourceFile"] is None)
		assert(response_json["edited"] == True)

	def test_create_workout_without_name(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileWorkoutListResource, username="creator")
		datetime_start = dt.datetime.utcnow()
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "name":"", "startAt":"{0}".format(startAt), "distance":1234, "duration":198, "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 4)
		assert(response_json["name"] == "Running")

	def test_create_workout_with_nonexistant_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileWorkoutListResource, username="creator")
		datetime_start = dt.datetime.utcnow()
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "name":"", "startAt":"{0}".format(startAt), "distance":1234, "duration":198, "categoryID":99 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Workout category not found")

	def test_create_workout_with_non_utc_startdate(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileWorkoutListResource, username="creator")
		now = dt.datetime.utcnow()
		datetime_start = dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone(dt.timedelta(hours=2)))
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S%z")
		utcStartAt = (datetime_start - datetime_start.utcoffset()).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "name":"My run", "startAt":"{0}".format(startAt), "distance":1234, "duration":198, "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["startAt"] == utcStartAt)


@pytest.mark.usefixtures('db')
class TestProfileWorkoutResource:

	def setup(self): # register some workouts
		cat1 = WorkoutCategoryModel('Running', True)
		cat1.save(commit=False)
		cat2 = WorkoutCategoryModel('Hiking', True)
		cat2.save()
		now = dt.datetime.utcnow()
		WorkoutModel(1, cat1, "Run 1", now - dt.timedelta(days=1), 3456, 201, 12, 'path/run1.gpx', False).save(commit=False)
		WorkoutModel(1, cat2, "Hike 1", now - dt.timedelta(days=3), 12345, 2340, 1102, None, False).save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_workout_not_logged_in(self, api, client):
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_workout_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["id"] == 2)

	def test_get_nonexistant_workout(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=99)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["workout"] is not None)

	def test_get_workout_for_another_user(self, api, client):
		register_confirmed_user("test", "test@test.com", "pwd")
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["workout"] is not None)

	def test_update_workout_not_logged_in(self, api, client):
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		response = client.put(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_update_workout_for_another_user(self, api, client):
		register_confirmed_user("test", "test@test.com", "pwd")
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=2)
		now = dt.datetime.utcnow()
		startAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.put(url, data={ "name":"My run", "startAt":"{0}".format(startAt), "distance":1234, "duration":198, "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"] is not None)

	def test_update_workout(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		now = dt.datetime.utcnow()
		startAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.put(url, data={ "name":"New name", "startAt":"{0}".format(startAt), "distance":4321, "duration":222, "climb":99, "categoryID":2, "edited":True }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 1)
		assert(response_json["name"] == "New name")
		assert(response_json["startAt"] == startAt)
		assert(response_json["distance"] == 4321)
		assert(response_json["duration"] == 222)
		assert(response_json["climb"] == 99)
		assert(response_json["categoryName"] == "Hiking")
		assert(response_json["resourceFile"] == "run1.gpx")
		assert(response_json["edited"] == True)

	def test_update_workout_with_nonexisting_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		now = dt.datetime.utcnow()
		startAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.put(url, data={ "name":"", "startAt":"{0}".format(startAt), "distance":4321, "duration":222, "climb":99, "categoryID":99 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Workout category not found")

	def test_update_workout_with_non_utc_timestamp(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		now = dt.datetime.utcnow()
		datetime_start = dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone(dt.timedelta(hours=2)))
		utcStartAt = (datetime_start - datetime_start.utcoffset()).strftime("%Y-%m-%dT%H:%M:%S+00:00")

		response = client.put(url, data={ "name":"", "startAt":"{0}".format(utcStartAt), "distance":4321, "duration":222, "climb":99, "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["startAt"] == utcStartAt)

	def test_post_workout_not_supported(self, api, client):
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_workout_not_supported(self, api, client):
		url = api.url_for(ProfileWorkoutResource, username="jonny", workout_id=1)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

@pytest.mark.usefixtures('db')
class TestProfileWorkoutGpxResource:
	def setup(self):
		cat1 = WorkoutCategoryModel('Running', True)
		cat1.save(commit=False)
	
	def teardown(self):
		try:
			tmp_filename = os.path.join(current_app.config["GPX_UPLOAD_DIR"], "jonny_test.gpx")
			os.remove(tmp_filename)
		except:
			pass
		try:
			filename = os.path.join(current_app.config["GPX_UPLOAD_DIR"], "jonny_workout_1.gpx")
			os.remove(filename)
		except:
			pass
		try:
			tmp_filename = os.path.join(current_app.config["GPX_UPLOAD_DIR"], "jonny_test.tcx")
			os.remove(tmp_filename)
		except:
			pass
		try:
			filename = os.path.join(current_app.config["GPX_UPLOAD_DIR"], "jonny_workout_1.tcx")
			os.remove(filename)
		except:
			pass

	def get_dummy_gpx_file(self):
		gpxStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><gpx xmlns=\"http://www.topografix.com/GPX/1/1\" version=\"1.1\" creator=\"Polar Ignite\">"
		gpxStr += "<metadata><author><name>Polar</name></author><time>2020-04-29T18:11:26.826Z</time></metadata><trk><trkseg>"
		gpxStr += "<trkpt lat=\"63.60100167\" lon=\"10.99771167\"><ele>15.0</ele><time>2020-04-29T18:11:26.826Z</time></trkpt>"
		gpxStr += "<trkpt lat=\"63.60100167\" lon=\"10.99771167\"><ele>15.0</ele><time>2020-04-29T18:11:27.827Z</time></trkpt>"
		gpxStr += "<trkpt lat=\"63.600985\" lon=\"10.99769833\"><ele>14.0</ele><time>2020-04-29T18:11:28.827Z</time></trkpt></trkseg></trk></gpx>"
		return io.BytesIO(bytearray(str.encode(gpxStr)))

	def get_dummy_tcx_file(self):
		tcxStr = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><TrainingCenterDatabase xsi:schemaLocation=\"http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd\" "
		tcxStr += "xmlns:ns5=\"http://www.garmin.com/xmlschemas/ActivityGoals/v1\" xmlns:ns3=\"http://www.garmin.com/xmlschemas/ActivityExtension/v2\" xmlns:ns2=\"http://www.garmin.com/xmlschemas/UserProfile/v2\" "
		tcxStr += "xmlns=\"http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:ns4=\"http://www.garmin.com/xmlschemas/ProfileExtension/v1\">"
		tcxStr += "<Activities><Activity Sport=\"Running\"><Id>2020-06-30T04:49:19.000Z</Id><Lap StartTime=\"2020-06-30T04:49:19.000Z\"><TotalTimeSeconds>284.0</TotalTimeSeconds>"
		tcxStr += "<DistanceMeters>1000.0</DistanceMeters><MaximumSpeed>3.825999975204468</MaximumSpeed><Calories>86</Calories><Intensity>Active</Intensity><TriggerMethod>Manual</TriggerMethod>"
		tcxStr += "<Track><Trackpoint><Time>2020-06-30T04:49:19.000Z</Time><Position><LatitudeDegrees>63.47279107198119</LatitudeDegrees><LongitudeDegrees>10.90274571441114</LongitudeDegrees></Position>"
		tcxStr += "<AltitudeMeters>12.600000381469727</AltitudeMeters><DistanceMeters>0.0</DistanceMeters></Trackpoint>"
		tcxStr += "<Trackpoint><Time>2020-06-30T04:49:25.000Z</Time><Position><LatitudeDegrees>63.472980335354805</LatitudeDegrees><LongitudeDegrees>10.902920477092266</LongitudeDegrees></Position>"
		tcxStr += "<AltitudeMeters>12.600000381469727</AltitudeMeters><DistanceMeters>23.229999542236328</DistanceMeters></Trackpoint>"
		tcxStr += "<Trackpoint><Time>2020-06-30T04:49:31.000Z</Time><Position><LatitudeDegrees>63.47312391735613</LatitudeDegrees><LongitudeDegrees>10.903240581974387</LongitudeDegrees></Position>"
		tcxStr += "<AltitudeMeters>12.600000381469727</AltitudeMeters><DistanceMeters>46.0</DistanceMeters></Trackpoint></Track></Lap>"
		tcxStr += "<Creator xsi:type=\"Device_t\"><Name>Forerunner 630</Name><UnitId>3918934328</UnitId><ProductID>2156</ProductID>"
		tcxStr += "<Version><VersionMajor>8</VersionMajor><VersionMinor>10</VersionMinor><BuildMajor>0</BuildMajor><BuildMinor>0</BuildMinor></Version>"
		tcxStr += "</Creator></Activity></Activities>"
		tcxStr += "<Author xsi:type=\"Application_t\"><Name>Connect Api</Name><Build>"
		tcxStr += "<Version><VersionMajor>0</VersionMajor><VersionMinor>0</VersionMinor><BuildMajor>0</BuildMajor><BuildMinor>0</BuildMinor></Version></Build>"
		tcxStr += "<LangID>en</LangID><PartNumber>006-D2449-00</PartNumber></Author></TrainingCenterDatabase>"
		return io.BytesIO(bytearray(str.encode(tcxStr)))

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.post(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_upload_gpx_not_logged_in(self, api, client):
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.post(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_upload_gpx_for_another_user(self, api, client):
		register_confirmed_user("test", "test@test.com", "pwd")
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="test", category_id=1)
		response = client.post(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Profile not found")

	def test_upload_gpx(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		fileinfo = {"gpxfile" : (self.get_dummy_gpx_file(), 'test.gpx')}
		response = client.post(url, data=fileinfo, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 1)
		assert(response_json["name"] == "[Place name] Running")
		assert(response_json["duration"] == 1.0)
		assert(response_json["distance"] == 2.0)
		assert(response_json["climb"] == 0)
		assert(response_json["resourceFile"] == "jonny_workout_1.gpx")
		assert(response_json["categoryName"] == "Running")

	def test_upload_tcx(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		fileinfo = {"gpxfile" : (self.get_dummy_tcx_file(), 'test.tcx')}
		response = client.post(url, data=fileinfo, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 1)
		assert(response_json["name"] == "[Place name] Running")
		assert(response_json["duration"] == 12)
		assert(response_json["distance"] == 45)
		assert(response_json["climb"] == 0)
		assert(response_json["resourceFile"] == "jonny_workout_1.tcx")
		assert(response_json["categoryName"] == "Running")

	def test_upload_with_nonexistant_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=99)
		fileinfo = {"gpxfile" : (self.get_dummy_tcx_file(), 'test.tcx')}
		response = client.post(url, data=fileinfo, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Workout category not found")

	def test_upload_gpx_invalid_file_label(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		fileinfo = {"filelabel" : (io.BytesIO(b"abcdef"), 'test.gpx')}
		response = client.post(url, data=fileinfo, headers=get_authorization_header(token))
		assert(response.status_code == 400)

	def test_upload_gpx_invalid_file_extension(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		fileinfo = {"gpxfile" : (io.BytesIO(b"abcdef"), 'test.abc')}
		response = client.post(url, data=fileinfo, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Workout filename invalid.")

	def test_upload_gpx_with_no_file(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.post(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["workout"][0] == "Workout file not provided.")

	def test_put_gpx_not_supported(self, api, client):
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_get_gpx_not_supported(self, api, client):
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_not_supported(self, api, client):
		url = api.url_for(ProfileWorkoutGpxResource, username="jonny", category_id=1)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
