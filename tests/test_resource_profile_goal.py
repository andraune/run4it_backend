import pytest
import datetime as dt
from run4it.api.goal import ProfileGoalListResource, ProfileGoalResource, GoalCategoryModel, GoalModel
from .helpers import get_response_json, register_confirmed_user, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestProfileGoalListResource:

	def setup(self): # register some goals
		cat1 = GoalCategoryModel('RunDistance', 'km')
		cat1.save(commit=False)
		cat2 = GoalCategoryModel('Weight target', 'kg')
		cat2.save()
		now = dt.datetime.utcnow()
		future_goal = GoalModel(1, cat1, now + dt.timedelta(days=2), now + dt.timedelta(days=3), 0, 2, 0)
		future_goal.save(commit=False)
		active_goal1 = GoalModel(1, cat1, now + dt.timedelta(days=-2), now + dt.timedelta(days=1), 0, 2, 1)
		active_goal2 = GoalModel(1, cat2, now + dt.timedelta(days=-2), now + dt.timedelta(days=2), 70, 68, 68)
		active_goal1.save(commit=False)
		active_goal2.save(commit=False)
		expired_goal1 = GoalModel(1, cat1, now + dt.timedelta(days=-10), now + dt.timedelta(days=-2), 0, 2, 0) # incomplete
		expired_goal2 = GoalModel(1, cat1, now + dt.timedelta(days=-8), now + dt.timedelta(days=-3), 0, 2, 2) # complete
		expired_goal1.save(commit=False)
		expired_goal2.save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_goals_not_logged_in(self, api, client):
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_goals_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 2) #active goals is default
		assert(response_json[1]['id'] == 3)

	def test_get_goals_filter_active(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="active")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 2)
		assert(response_json[1]['id'] == 3)

	def test_get_goals_filter_future(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="future")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 1)

	def test_get_goals_filter_expired(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="expired")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 4)
		assert(response_json[1]['id'] == 5)

	def test_get_goals_filter_completed(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="completed")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 5)

	def test_get_goals_filter_incompleted(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 4)

	def test_get_goals_duration(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json[0]['duration'] == 8)

	def test_get_goals_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json[0]['categoryName'] == 'RunDistance')
		assert(response_json[0]['categoryUnit'] == 'km')

	def test_create_goal_not_logged_in(self, api, client):
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.post(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_create_future_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		datetime_start = dt.datetime.utcnow() + dt.timedelta(days=2)
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		endAt = (datetime_start + dt.timedelta(days=duration)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":23.4, "startAt": "{0}".format(startAt), "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 6) # five created in setup
		assert(response_json["startAt"] == startAt)
		assert(response_json["endAt"] == endAt)
		assert(response_json["duration"] == duration)
		assert(response_json["startValue"] == 11.2)
		assert(response_json["targetValue"] == 23.4)
		assert(response_json["categoryName"] == "RunDistance")
		assert(response_json["categoryUnit"] == "km")
		assert(response.headers["Location"] == api.url_for(ProfileGoalResource, username="creator",goal_id=6, _external=True))

	def test_create_ongoing_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		datetime_start = dt.datetime.utcnow() - dt.timedelta(days=2)
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		endAt = (datetime_start + dt.timedelta(days=duration)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":23.4, "startAt": "{0}".format(startAt), "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["startAt"] == startAt)
		assert(response_json["endAt"] == endAt)
		assert(response_json["duration"] == duration)

	def test_create_expired_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		datetime_start = dt.datetime.utcnow() - dt.timedelta(days=6)
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":23.4, "startAt": "{0}".format(startAt), "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"][0] == "Goal already expired")

	def test_create_goal_with_startvalue_equal_to_target_value(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		datetime_start = dt.datetime.utcnow() + dt.timedelta(days=2)
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":11.2, "startAt": "{0}".format(startAt), "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"][0] == "Goal target value equals start value")

	def test_create_goal_with_nonexistant_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		datetime_start = dt.datetime.utcnow() + dt.timedelta(days=2)
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":12.2, "startAt": "{0}".format(startAt), "categoryID":99 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"][0] == "Goal category not found")

	def test_create_goal_with_non_utc_startdate(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "creator", "creator@user.no", "pwd")
		url = api.url_for(ProfileGoalListResource, username="creator")
		now = dt.datetime.utcnow()
		datetime_start = dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone(dt.timedelta(hours=2)))
		startAt = datetime_start.strftime("%Y-%m-%dT%H:%M:%S%z")
		utcStartAt = (datetime_start - datetime_start.utcoffset()).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		duration = 4
		utcEndAt = (datetime_start - datetime_start.utcoffset() + dt.timedelta(days=duration)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.post(url, data={ "duration":duration, "startValue":11.2, "targetValue":12.2, "startAt": "{0}".format(startAt), "categoryID":1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["startAt"] == utcStartAt)
		assert(response_json["endAt"] == utcEndAt)
	

@pytest.mark.usefixtures('db')
class TestProfileGoalResource:

	def setup(self): # register some goals
		cat1 = GoalCategoryModel('RunDistance', 'km')
		cat1.save(commit=False)
		cat2 = GoalCategoryModel('CrawlDistance', 'm')
		cat2.save()
		now = dt.datetime.utcnow()
		future_goal = GoalModel(1, cat1, now + dt.timedelta(days=2), now + dt.timedelta(days=3), 0, 2, 0)
		future_goal.save(commit=False)
		active_goal = GoalModel(1, cat1, now + dt.timedelta(days=-2), now + dt.timedelta(days=1), 0, 2, 1)
		active_goal.save(commit=False)
		expired_goal = GoalModel(1, cat1, now + dt.timedelta(days=-10), now + dt.timedelta(days=-2), 0, 2, 0)
		expired_goal.save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_goal_not_logged_in(self, api, client):
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_goal_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["id"] == 2)

	def test_get_nonexistant_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=99)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["goal"] is not None)

	def test_get_goal_for_another_user(self, api, client):
		register_confirmed_user("test", "test@test.com", "pwd")
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=2)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["goal"] is not None)

	def test_update_goal_not_logged_in(self, api, client):
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		response = client.put(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_update_goal_for_another_user(self, api, client):
		register_confirmed_user("test", "test@test.com", "pwd")
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=2)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":2.1, "startAt": "{0}".format(newStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"] is not None)

	def test_update_future_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		newEndAt = (now + dt.timedelta(days=newDuration)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":2.1, "startAt": "{0}".format(newStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 1)
		assert(response_json["startAt"] == newStartAt)
		assert(response_json["endAt"] == newEndAt)
		assert(response_json["duration"] == 1)
		assert(response_json["startValue"] == 1.2)
		assert(response_json["targetValue"] == 2.1)
		assert(response_json["categoryName"] == "CrawlDistance")
		assert(response_json["categoryUnit"] == "m")

	def test_update_ongoing_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=2)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":2.1, "startAt": "{0}".format(newStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 2)

	def test_update_expired_goal(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=3)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":2.1, "startAt": "{0}".format(newStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"][0] == "Goal already expired")
	
	def test_update_goal_with_nonexisting_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":2.1, "startAt": "{0}".format(newStartAt), "categoryID":22 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"][0] == "Goal category not found")	

	def test_update_goal_with_non_utc_timestamp(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		now = dt.datetime.utcnow()
		datetime_start = dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone(dt.timedelta(hours=2)))
		utcStartAt = (datetime_start - datetime_start.utcoffset()).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		new_duration = 3
		utcEndAt = (datetime_start - datetime_start.utcoffset() + dt.timedelta(days=new_duration)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
		response = client.put(url, data={ "duration":new_duration, "startValue":1.2, "targetValue":2.2, "startAt": "{0}".format(utcStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["startAt"] == utcStartAt)
		assert(response_json["endAt"] == utcEndAt)

	def test_update_goal_with_startvalue_equal_to_endvalue(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		now = dt.datetime.utcnow()
		newStartAt = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
		newDuration = 1
		response = client.put(url, data={ "duration":newDuration, "startValue":1.2, "targetValue":1.2, "startAt": "{0}".format(newStartAt), "categoryID":2 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["goal"] is not None)	

	def test_post_goal_not_supported(self, api, client):
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_goal_not_supported(self, api, client):
		url = api.url_for(ProfileGoalResource, username="jonny", goal_id=1)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
